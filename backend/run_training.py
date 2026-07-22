import argparse
from pathlib import Path

import torch
from torch.utils.data import DataLoader

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
    data_loader = DataLoader(
        dataset,
        batch_size=int(training_config["batch_size"]),
        shuffle=True,
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
    print(f"Latent dimensions: {model_config['latent_dim']}")

    history = train_vae(
        model=model,
        data_loader=data_loader,
        optimizer=optimizer,
        device=device,
        epochs=int(training_config["epochs"]),
    )

    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "experiment_name": config.get("experiment_name"),
            "model_config": model_config,
            "training_config": training_config,
            "seed": seed,
            "training_history": history,
        },
        checkpoint_path,
    )

    print(f"Model checkpoint saved to: {checkpoint_path}")


if __name__ == "__main__":
    main()
