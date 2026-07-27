import argparse
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Dataset, random_split

from backend.config import load_experiment_config
from backend.dataset import FingerprintDataset
from backend.model import MolecularVAE
from backend.training import train_vae


def parse_arguments() -> argparse.Namespace:
    """Read the selected YAML experiment configuration path."""
    parser = argparse.ArgumentParser(description="Train the Fingerprint VAE.")
    parser.add_argument(
        "--config",
        default="configs/fingerprint_vae.yaml",
        help="Path to the experiment YAML configuration.",
    )
    return parser.parse_args()

def split_dataset(
    dataset: FingerprintDataset,
    validation_fraction: float,
    seed: int,
) -> tuple[Dataset, Dataset]:
    """Create a deterministic non-empty train and validation split."""
    if not 0 < validation_fraction < 1:
        raise ValueError(
            "validation_fraction must be greater than 0 and less than 1."
        )

    if len(dataset) < 2:
        raise ValueError(
            "At least two molecules are required for train/validation splitting."
        )

    validation_size = max(1, round(len(dataset) * validation_fraction))
    validation_size = min(validation_size, len(dataset) - 1)
    train_size = len(dataset) - validation_size

    split_generator = torch.Generator().manual_seed(seed)

    return random_split(
        dataset,
        [train_size, validation_size],
        generator=split_generator,
    )


def main() -> None:
    """Load molecular fingerprints, train the VAE, and save its checkpoint."""
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
    checkpoint_path = project_root / artifact_config["checkpoint_path"]

    dataset = FingerprintDataset(fingerprint_path)
    train_dataset, validation_dataset = split_dataset(
     dataset=dataset,
        validation_fraction=float(data_config["validation_fraction"]),
        seed=seed,
    )

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
    print(f"Latent dimensions: {model_config['latent_dim']}")

    
    history = train_vae(
        model=model,
        data_loader=train_data_loader,
        optimizer=optimizer,
        device=device,
        epochs=int(training_config["epochs"]),
        validation_data_loader=validation_data_loader,
    )

    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "experiment_name": config.get("experiment_name"),
            "model_config": model_config,
            "training_config": training_config,
            "seed": seed,
            "dataset_sizes": {
                "total": len(dataset),
                "training": len(train_dataset),
                "validation": len(validation_dataset),
            },
            "training_history": history,
        },
        checkpoint_path,
    )

    print(f"Model checkpoint saved to: {checkpoint_path}")


if __name__ == "__main__":
    main()
