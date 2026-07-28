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




def main() -> None:
    project_root = Path(__file__).parent.parent
    input_path = project_root / "data" / "qm9_sample.csv"
    output_directory = project_root / "data" / "processed"  

    metadata, fingerprints, rejected = preprocess_dataset(
        input_path = input_path, 
        output_directory =  output_directory,
        )
    
    print("Preprocessing complete.")
    print(f"Valid molecules: {len(metadata)}")
    print(f"Rejected molecules: {rejected}")
    print(f"Fingerprint shape: {fingerprints.shape}")
    print(f"Fingerprint width: {FINGERPRINT_BITS}")
    print(f"Output directory: {output_directory}")

if __name__ == "__main__":
    main() 