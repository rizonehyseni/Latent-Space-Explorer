"""Preprocess a configured molecular dataset and create reproducible splits."""

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from backend.preprocessing import (
    FINGERPRINT_BITS, 
    preprocess_dataset
    )

from backend.splits import (
    create_split_indices,
    save_split_indices,
)

def parse_arguments() -> argparse.Namespace:
    """Read the QM9 preprocessing configuration path."""
    parser = argparse.ArgumentParser(
        description="Preprocess QM9 molecules and create dataset splits."
    )
    parser.add_argument(
        "--config",
        default="configs/qm9_processing.yaml",
        help="Path to the QM9 preprocessing YAML configuration.",
    )
    return parser.parse_args()

def load_processing_config(config_path: Path) -> dict[str, Any]:
    """Load and validate the QM9 preprocessing configuration."""
    if not config_path.is_file():
        raise FileNotFoundError(
            f"Preprocessing configuration was not found: {config_path}"
        )

    with config_path.open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    if not isinstance(config, dict):
        raise ValueError(
            "Preprocessing configuration must contain a YAML mapping."
        )

    required_sections = {"dataset", "splits"}
    missing_sections = required_sections.difference(config)

    if missing_sections:
        missing = ", ".join(sorted(missing_sections))
        raise ValueError(
            f"Preprocessing configuration is missing required sections: {missing}"
        )

    return config

def resolve_project_path(project_root: Path, path_value: str) -> Path:
    """Resolve configuration paths relative to the project root."""
    path = Path(path_value)
    return path if path.is_absolute() else project_root / path


def main() -> None:
    """Preprocess QM9 fingerprints and save deterministic data splits."""
    arguments = parse_arguments()
    project_root = Path(__file__).resolve().parent.parent

    config_path = Path(arguments.config)
    if not config_path.is_absolute():
        config_path = project_root / config_path

    config = load_processing_config(config_path)

    dataset_config = config["dataset"]
    split_config = config["splits"]

    input_path = resolve_project_path(
        project_root,
        dataset_config["input_csv"],
    )
    output_directory = resolve_project_path(
        project_root,
        dataset_config["output_directory"],
    )

    metadata, fingerprints, rejected_molecules = preprocess_dataset(
        input_path=input_path,
        output_directory=output_directory,
    )

    split_indices = create_split_indices(
        dataset_size=len(metadata),
        train_fraction=float(split_config["train_fraction"]),
        validation_fraction=float(split_config["validation_fraction"]),
        test_fraction=float(split_config["test_fraction"]),
        seed=int(split_config["seed"]),
    )

    split_path = output_directory / "split_indices.npz"
    save_split_indices(split_indices, split_path)

    summary = {
        "input_path": str(input_path.relative_to(project_root)),
        "output_directory": str(output_directory.relative_to(project_root)),
        "valid_molecules": len(metadata),
        "rejected_molecules": rejected_molecules,
        "fingerprint_shape": list(fingerprints.shape),
        "fingerprint_width": FINGERPRINT_BITS,
        "split_seed": int(split_config["seed"]),
        "splits": {
            name: len(indices)
            for name, indices in split_indices.items()
        },
    }

    summary_path = output_directory / "preparation_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    print("QM9 preprocessing complete.")
    print(f"Input molecules: {len(metadata) + rejected_molecules}")
    print(f"Valid molecules: {len(metadata)}")
    print(f"Rejected molecules: {rejected_molecules}")
    print(f"Fingerprint shape: {fingerprints.shape}")
    print(f"Fingerprint width: {FINGERPRINT_BITS}")
    print(f"Training split: {len(split_indices['train'])}")
    print(f"Validation split: {len(split_indices['validation'])}")
    print(f"Test split: {len(split_indices['test'])}")
    print(f"Output directory: {output_directory}")
    print(f"Split indices: {split_path}")
    print(f"Preparation summary: {summary_path}")



if __name__ == "__main__":
    main() 