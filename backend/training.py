from collections.abc import Iterable
from copy import deepcopy

import torch
from torch import nn
from torch.nn import functional as functional


def vae_loss(
    reconstruction_logits: torch.Tensor,
    fingerprints: torch.Tensor,
    mu: torch.Tensor,
    log_var: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Calculate reconstruction and KL-divergence losses for a VAE."""
    reconstruction_loss = functional.binary_cross_entropy_with_logits(
        reconstruction_logits,
        fingerprints,
        reduction="sum",
    )

    kl_divergence = -0.5 * torch.sum(
        1 + log_var - mu.pow(2) - log_var.exp()
    )

    total_loss = reconstruction_loss + kl_divergence

    return total_loss, reconstruction_loss, kl_divergence

@torch.no_grad()
def evaluate_vae(
    model: nn.Module,
    data_loader: Iterable[torch.Tensor],
    device: torch.device,
) -> dict[str, float]:
    """Evaluate VAE losses using the deterministic latent mean vector."""
    model.eval()

    total_loss = 0.0
    total_reconstruction_loss = 0.0
    total_kl_divergence = 0.0
    total_samples = 0

    for fingerprints in data_loader:
        fingerprints = fingerprints.to(device)

        mu, log_var = model.encode(fingerprints)
        reconstruction_logits = model.decode(mu)

        loss, reconstruction_loss, kl_divergence = vae_loss(
            reconstruction_logits,
            fingerprints,
            mu,
            log_var,
        )

        batch_size = fingerprints.size(0)
        total_samples += batch_size
        total_loss += loss.item()
        total_reconstruction_loss += reconstruction_loss.item()
        total_kl_divergence += kl_divergence.item()

    if total_samples == 0:
        raise ValueError("Cannot evaluate an empty data loader.")

    return {
        "loss": total_loss / total_samples,
        "reconstruction_loss": total_reconstruction_loss / total_samples,
        "kl_divergence": total_kl_divergence / total_samples,
    }

def train_vae(
    model: nn.Module,
    data_loader: Iterable[torch.Tensor],
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    epochs: int,
    validation_data_loader: Iterable[torch.Tensor] | None = None,
) -> dict[str, object]:
    """Train a VAE and retain the checkpoint with best validation loss."""
    model.to(device)

    training_history: list[dict[str, float]] = []
    best_epoch: int | None = None
    best_validation_loss: float | None = None
    best_model_state_dict: dict[str, torch.Tensor] | None = None

    for epoch in range(1, epochs + 1):
        model.train()

        total_loss = 0.0
        total_reconstruction_loss = 0.0
        total_kl_divergence = 0.0
        total_samples = 0

        for fingerprints in data_loader:
            fingerprints = fingerprints.to(device)

            optimizer.zero_grad()

            reconstruction_logits, mu, log_var = model(fingerprints)

            loss, reconstruction_loss, kl_divergence = vae_loss(
                reconstruction_logits,
                fingerprints,
                mu,
                log_var,
            )

            loss.backward()
            optimizer.step()

            batch_size = fingerprints.size(0)
            total_samples += batch_size
            total_loss += loss.item()
            total_reconstruction_loss += reconstruction_loss.item()
            total_kl_divergence += kl_divergence.item()

        epoch_metrics = {
            "epoch": float(epoch),
            "loss": total_loss / total_samples,
            "reconstruction_loss": total_reconstruction_loss / total_samples,
            "kl_divergence": total_kl_divergence / total_samples,
        }

        if validation_data_loader is not None:
            validation_metrics = evaluate_vae(
                model=model,
                data_loader=validation_data_loader,
                device=device,
            )

            epoch_metrics.update(
                {
                    "validation_loss": validation_metrics["loss"],
                    "validation_reconstruction_loss": (
                        validation_metrics["reconstruction_loss"]
                    ),
                    "validation_kl_divergence": (
                        validation_metrics["kl_divergence"]
                    ),
                }
            )

            if (
                best_validation_loss is None
                or validation_metrics["loss"] < best_validation_loss
            ):
                best_epoch = epoch
                best_validation_loss = validation_metrics["loss"]
                best_model_state_dict = deepcopy(model.state_dict())

        training_history.append(epoch_metrics)

        print(
            f"Epoch {epoch}/{epochs} | "
            f"Loss: {epoch_metrics['loss']:.4f} | "
            f"Reconstruction: {epoch_metrics['reconstruction_loss']:.4f} | "
            f"KL: {epoch_metrics['kl_divergence']:.4f}"
        )

        if validation_data_loader is not None:
            print(
                "  Validation | "
                f"Loss: {epoch_metrics['validation_loss']:.4f} | "
                "Reconstruction: "
                f"{epoch_metrics['validation_reconstruction_loss']:.4f} | "
                f"KL: {epoch_metrics['validation_kl_divergence']:.4f}"
            )

    if best_model_state_dict is None:
        best_epoch = epochs
        best_model_state_dict = deepcopy(model.state_dict())

    return {
        "history": training_history,
        "best_epoch": best_epoch,
        "best_validation_loss": best_validation_loss,
        "best_model_state_dict": best_model_state_dict,
    }  