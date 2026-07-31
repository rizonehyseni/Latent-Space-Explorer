"""Export deterministic QM9 latent vectors from a trained Fingerprint VAE."""

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, TensorDataset

from backend.config import load_experiment_config
from backend.model import MolecularVAE
from backend.splits import validate_split_indices


REQUIRED_EXPORT_SECTIONS = {"data", "model", "export", "artifacts"}
REQUIRED_METADATA_COLUMNS = {"source_index", "id", "smiles"}


def parse_arguments() -> argparse.Namespace:
    """Read the selected latent-export configuration path."""
    parser = argparse.ArgumentParser(
        description="Export deterministic QM9 Fingerprint VAE latent vectors."
    )
    parser.add_argument(
        "--config",
        default="configs/qm9_latent_export.yaml",
        help="Path to the latent-export YAML configuration.",
    )
    return parser.parse_args()


def resolve_project_path(project_root: Path, path_value: str) -> Path:
    """Resolve a configuration path relative to the project root."""
    path = Path(path_value)
    return path if path.is_absolute() else project_root / path


def display_project_path(project_root: Path, path: Path) -> str:
    """Display project-relative paths when possible."""
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def load_split_indices(
    split_path: Path,
    dataset_size: int,
) -> dict[str, np.ndarray]:
    """Load and validate saved train, validation, and test indices."""
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


def create_split_labels(
    split_indices: dict[str, np.ndarray],
    dataset_size: int,
) -> np.ndarray:
    """Create one deterministic split label for every dataset row."""
    labels = np.full(dataset_size, "", dtype="<U10")

    for split_name, indices in split_indices.items():
        labels[indices] = split_name

    if np.any(labels == ""):
        raise ValueError("Every molecule must receive exactly one split label.")

    return labels


def load_metadata(metadata_path: Path, dataset_size: int) -> pd.DataFrame:
    """Load metadata and verify that it aligns with fingerprint rows."""
    if not metadata_path.is_file():
        raise FileNotFoundError(
            f"Molecule metadata artifact was not found: {metadata_path}"
        )

    metadata = pd.read_csv(metadata_path)
    missing_columns = REQUIRED_METADATA_COLUMNS.difference(metadata.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"Molecule metadata is missing required columns: {missing}"
        )

    if len(metadata) != dataset_size:
        raise ValueError(
            "Metadata row count must match the fingerprint dataset size."
        )

    return metadata


def load_fingerprints(fingerprint_path: Path) -> np.ndarray:
    """Load the preprocessed fingerprint matrix as float32 values."""
    if not fingerprint_path.is_file():
        raise FileNotFoundError(
            f"Fingerprint artifact was not found: {fingerprint_path}"
        )

    fingerprints = np.load(fingerprint_path)

    if fingerprints.ndim != 2:
        raise ValueError(
            "Fingerprint artifact must be a 2D matrix with shape "
            "(molecules, fingerprint_bits)."
        )

    if len(fingerprints) == 0:
        raise ValueError("Fingerprint artifact is empty.")

    return fingerprints.astype(np.float32)


def load_trained_model(
    checkpoint_path: Path,
    model_config: dict[str, Any],
    device: torch.device,
) -> tuple[MolecularVAE, dict[str, Any]]:
    """Load the selected Fingerprint VAE checkpoint."""
    if not checkpoint_path.is_file():
        raise FileNotFoundError(
            f"Model checkpoint was not found: {checkpoint_path}"
        )

    checkpoint = torch.load(checkpoint_path, map_location=device)

    if "model_state_dict" not in checkpoint:
        raise ValueError("Model checkpoint does not contain model_state_dict.")

    checkpoint_model_config = checkpoint.get("model_config")

    if checkpoint_model_config != model_config:
        raise ValueError(
            "Checkpoint model configuration does not match the export "
            "configuration."
        )

    model = MolecularVAE(
        input_dim=int(model_config["input_dim"]),
        hidden_dim=int(model_config["hidden_dim"]),
        latent_dim=int(model_config["latent_dim"]),
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()

    return model, checkpoint


def encode_latent_means(
    model: MolecularVAE,
    fingerprints: np.ndarray,
    batch_size: int,
    device: torch.device,
) -> np.ndarray:
    """Encode every fingerprint into its deterministic latent mean vector."""
    dataset = TensorDataset(torch.from_numpy(fingerprints))
    data_loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

    latent_batches: list[np.ndarray] = []

    with torch.no_grad():
        for (fingerprint_batch,) in data_loader:
            fingerprint_batch = fingerprint_batch.to(device)
            latent_means, _ = model.encode(fingerprint_batch)
            latent_batches.append(latent_means.cpu().numpy())

    return np.vstack(latent_batches).astype(np.float32)


def export_latent_space_artifacts(
    fingerprint_path: Path,
    metadata_path: Path,
    split_indices_path: Path,
    checkpoint_path: Path,
    latent_vectors_path: Path,
    latent_metadata_path: Path,
    manifest_path: Path,
    model_config: dict[str, Any],
    batch_size: int,
    device: torch.device,
    project_root: Path,
) -> dict[str, Any]:
    """Export aligned latent vectors, metadata, and provenance information."""
    fingerprints = load_fingerprints(fingerprint_path)

    if fingerprints.shape[1] != int(model_config["input_dim"]):
        raise ValueError(
            "Fingerprint width does not match the configured model input_dim."
        )

    metadata = load_metadata(metadata_path, len(fingerprints))
    split_indices = load_split_indices(split_indices_path, len(fingerprints))
    split_labels = create_split_labels(split_indices, len(fingerprints))

    model, checkpoint = load_trained_model(
        checkpoint_path=checkpoint_path,
        model_config=model_config,
        device=device,
    )

    latent_vectors = encode_latent_means(
        model=model,
        fingerprints=fingerprints,
        batch_size=batch_size,
        device=device,
    )

    if latent_vectors.shape != (
        len(fingerprints),
        int(model_config["latent_dim"]),
    ):
        raise ValueError("Exported latent-vector shape is invalid.")

    latent_metadata = metadata.copy()
    latent_metadata.insert(0, "latent_row", np.arange(len(latent_metadata)))
    latent_metadata["split"] = split_labels

    latent_vectors_path.parent.mkdir(parents=True, exist_ok=True)
    latent_metadata_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    np.save(latent_vectors_path, latent_vectors)
    latent_metadata.to_csv(latent_metadata_path, index=False)

    manifest = {
        "artifact_schema_version": 1,
        "latent_representation": "encoder_mean_mu",
        "dataset_size": len(fingerprints),
        "latent_dimensions": int(model_config["latent_dim"]),
        "export_batch_size": batch_size,
        "checkpoint": {
            "path": display_project_path(project_root, checkpoint_path),
            "experiment_name": checkpoint.get("experiment_name"),
            "best_epoch": checkpoint.get("best_epoch"),
            "best_validation_loss": checkpoint.get("best_validation_loss"),
        },
        "inputs": {
            "fingerprint_path": display_project_path(
                project_root,
                fingerprint_path,
            ),
            "metadata_path": display_project_path(project_root, metadata_path),
            "split_indices_path": display_project_path(
                project_root,
                split_indices_path,
            ),
        },
        "outputs": {
            "latent_vectors_path": display_project_path(
                project_root,
                latent_vectors_path,
            ),
            "latent_metadata_path": display_project_path(
                project_root,
                latent_metadata_path,
            ),
        },
        "split_sizes": {
            split_name: int(len(indices))
            for split_name, indices in split_indices.items()
        },
        "metadata_columns": latent_metadata.columns.tolist(),
    }

    manifest_path.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    return manifest


def main() -> None:
    """Export QM9 latent means and aligned molecule metadata."""
    arguments = parse_arguments()
    project_root = Path(__file__).resolve().parent.parent

    config_path = Path(arguments.config)
    if not config_path.is_absolute():
        config_path = project_root / config_path

    config = load_experiment_config(
        config_path,
        required_sections=REQUIRED_EXPORT_SECTIONS,
    )

    data_config = config["data"]
    model_config = config["model"]
    export_config = config["export"]
    artifact_config = config["artifacts"]

    fingerprint_path = resolve_project_path(
        project_root,
        data_config["fingerprint_path"],
    )
    metadata_path = resolve_project_path(
        project_root,
        data_config["metadata_path"],
    )
    split_indices_path = resolve_project_path(
        project_root,
        data_config["split_indices_path"],
    )
    checkpoint_path = resolve_project_path(
        project_root,
        artifact_config["checkpoint_path"],
    )
    latent_vectors_path = resolve_project_path(
        project_root,
        artifact_config["latent_vectors_path"],
    )
    latent_metadata_path = resolve_project_path(
        project_root,
        artifact_config["latent_metadata_path"],
    )
    manifest_path = resolve_project_path(
        project_root,
        artifact_config["manifest_path"],
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    manifest = export_latent_space_artifacts(
        fingerprint_path=fingerprint_path,
        metadata_path=metadata_path,
        split_indices_path=split_indices_path,
        checkpoint_path=checkpoint_path,
        latent_vectors_path=latent_vectors_path,
        latent_metadata_path=latent_metadata_path,
        manifest_path=manifest_path,
        model_config=model_config,
        batch_size=int(export_config["batch_size"]),
        device=device,
        project_root=project_root,
    )

    print(f"Export device: {device}")
    print(f"Exported molecules: {manifest['dataset_size']}")
    print(f"Latent dimensions: {manifest['latent_dimensions']}")
    print(
        "Latent vectors: "
        f"{project_root / manifest['outputs']['latent_vectors_path']}"
    )
    print(
        "Latent metadata: "
        f"{project_root / manifest['outputs']['latent_metadata_path']}"
    )
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()