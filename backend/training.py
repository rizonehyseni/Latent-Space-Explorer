from collections.abc import Iterable

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


def train_vae(
    model: nn.Module,
    data_loader: Iterable[torch.Tensor],
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    epochs: int,
) -> list[dict[str, float]]:
    """Train a VAE and return loss metrics for every epoch."""
    model.to(device)
    training_history: list[dict[str, float]] = []

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

        training_history.append(epoch_metrics)

        print(
            f"Epoch {epoch}/{epochs} | "
            f"Loss: {epoch_metrics['loss']:.4f} | "
            f"Reconstruction: {epoch_metrics['reconstruction_loss']:.4f} | "
            f"KL: {epoch_metrics['kl_divergence']:.4f}"
        )

    return training_history