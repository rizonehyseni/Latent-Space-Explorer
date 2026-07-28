import argparse
import json
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, Subset

from backend.config import load_experiment_config
from backend.dataset import FingerprintDataset
from backend.model import MolecularVAE
from backend.splits import validate_split_indices
from backend.training import evaluate_vae, train_vae



def parse_arguments() -> argparse.Namespace:
    """Read the selected YAML experiment configuration path."""
    parser = argparse.ArgumentParser(description="Train the Fingerprint VAE.")
    parser.add_argument(
        "--config",
        default="configs/qm9_fingerprint_vae.yaml",
        help="Path to the experiment YAML configuration.",
    )
    return parser.parse_args()


def load_split_indices(
    split_path: Path,
    dataset_size: int,
) -> dict[str, np.ndarray]:
    """Load and validate saved train, validation, and test split indices."""
    if not split_path.is_file():
        raise FileNotFoundError(
            f"Split index artifact was not found: {split_path}"
        )

    with np.load(split_path) as split_file:
        split_indices = {
            "train": split_file["train"],
            "validation": split_file["validation"],
            "test": split_file["test"],
        }

    validate_split_indices(split_indices, dataset_size)

    return split_indices


def main() -> None:
    """Train on QM9 data and evaluate the selected model on the test split."""
    arguments = parse_arguments()
    project_root = Path(__file__).resolve().parent.parent

    config_path = Path(arguments.config)
    if not config_path.is_absolute():
        config_path = project_root / config_path

    config = load_experiment_config(config_path)

    data_config = config["data"]
    model_config = config["model"]
    training_config = config["training"]
    artifact_config = config["artifacts"]

    seed = int(config.get("seed", 42))
    torch.manual_seed(seed)

    fingerprint_path = project_root / data_config["fingerprint_path"]
    split_indices_path = project_root / data_config["split_indices_path"]
    checkpoint_path = project_root / artifact_config["checkpoint_path"]
    results_path = project_root / artifact_config["results_path"]

    dataset = FingerprintDataset(fingerprint_path)
    split_indices = load_split_indices(
        split_path=split_indices_path,
        dataset_size=len(dataset),
    )

    train_dataset = Subset(dataset, split_indices["train"].tolist())
    validation_dataset = Subset(
        dataset,
        split_indices["validation"].tolist(),
    )
    test_dataset = Subset(dataset, split_indices["test"].tolist())

    batch_size = int(training_config["batch_size"])

    training_generator = torch.Generator().manual_seed(seed)

    train_data_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        generator=training_generator,
    )
    validation_data_loader = DataLoader(
        validation_dataset,
        batch_size=batch_size,
        shuffle=False,
    )
    test_data_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = MolecularVAE(
        input_dim=int(model_config["input_dim"]),
        hidden_dim=int(model_config["hidden_dim"]),
        latent_dim=int(model_config["latent_dim"]),
    )

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=float(training_config["learning_rate"]),
    )

    print(f"Training device: {device}")
    print(f"Molecules in dataset: {len(dataset)}")
    print(f"Training molecules: {len(train_dataset)}")
    print(f"Validation molecules: {len(validation_dataset)}")
    print(f"Test molecules: {len(test_dataset)}")
    print(f"Latent dimensions: {model_config['latent_dim']}")

    training_result = train_vae(
        model=model,
        data_loader=train_data_loader,
        optimizer=optimizer,
        device=device,
        epochs=int(training_config["epochs"]),
        validation_data_loader=validation_data_loader,
    )

    model.load_state_dict(training_result["best_model_state_dict"])
    model.to(device)

    test_metrics = evaluate_vae(
        model=model,
        data_loader=test_data_loader,
        device=device,
    )

    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    checkpoint = {
        "model_state_dict": model.state_dict(),
        "experiment_name": config.get("experiment_name"),
        "model_config": model_config,
        "training_config": training_config,
        "seed": seed,
        "dataset_sizes": {
            "total": len(dataset),
            "training": len(train_dataset),
            "validation": len(validation_dataset),
            "test": len(test_dataset),
        },
        "best_epoch": training_result["best_epoch"],
        "best_validation_loss": training_result["best_validation_loss"],
        "test_metrics": test_metrics,
        "training_history": training_result["history"],
    }

    torch.save(checkpoint, checkpoint_path)

    results = {
        "experiment_name": config.get("experiment_name"),
        "seed": seed,
        "dataset_sizes": checkpoint["dataset_sizes"],
        "best_epoch": training_result["best_epoch"],
        "best_validation_loss": training_result["best_validation_loss"],
        "test_metrics": test_metrics,
        "training_history": training_result["history"],
    }

    results_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )

    print(f"Best validation epoch: {training_result['best_epoch']}")
    print(
        "Best validation loss: "
        f"{training_result['best_validation_loss']:.4f}"
    )
    print(
        "Test loss: "
        f"{test_metrics['loss']:.4f} | "
        f"Reconstruction: {test_metrics['reconstruction_loss']:.4f} | "
        f"KL: {test_metrics['kl_divergence']:.4f}"
    )
    print(f"Model checkpoint saved to: {checkpoint_path}")
    print(f"Evaluation results saved to: {results_path}")



if __name__ == "__main__":
    main()
