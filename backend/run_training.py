from pathlib import Path

import torch
from torch.utils.data import DataLoader

from backend.dataset import FingerprintDataset
from backend.model import MolecularVAE
from backend.training import train_vae

LATENT_DIM = 16
BATCH_SIZE = 64
LEARNING_RATE = 1e-3
EPOCHS = 50
RANDOM_SEED = 42


def main() -> None:
    """Load molecular fingerprints, train the VAE, and save its checkpoint."""
    torch.manual_seed(RANDOM_SEED)

    project_root = Path(__file__).resolve().parent.parent
    fingerprint_path = project_root / "data" / "processed" / "morgan_fingerprints.npy"
    model_directory = project_root / "models"
    checkpoint_path = model_directory / "molecular_vae.pt"

    dataset = FingerprintDataset(fingerprint_path)
    data_loader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = MolecularVAE(latent_dim=LATENT_DIM)
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE,
    )

    print(f"Training device: {device}")
    print(f"Molecules in dataset: {len(dataset)}")
    print(f"Latent dimensions: {LATENT_DIM}")

    history = train_vae(
        model=model,
        data_loader=data_loader,
        optimizer=optimizer,
        device=device,
        epochs=EPOCHS,
    )

    model_directory.mkdir(parents=True, exist_ok=True)

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "latent_dim": LATENT_DIM,
            "input_dim": 2048,
            "training_history": history,
        },
        checkpoint_path,
    )

    print(f"Model checkpoint saved to: {checkpoint_path}")


if __name__ == "__main__":
    main()