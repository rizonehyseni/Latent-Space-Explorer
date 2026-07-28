"""Download and prepare a reproducible QM9 subset for later preprocessing."""

import argparse
import hashlib
import json
import tarfile
from pathlib import Path
from typing import Any
from urllib.request import urlretrieve

import pandas as pd
import yaml
from rdkit import Chem

def parse_arguments() -> argparse.Namespace:
    """Read the QM9 preparation configuration path."""
    parser = argparse.ArgumentParser(
        description="Download and prepare a deterministic QM9 subset."
    )
    parser.add_argument(
        "--config",
        default="configs/qm9_subset.yaml",
        help="Path to the QM9 preparation YAML configuration.",
    )
    return parser.parse_args()


def load_dataset_config(config_path: Path) -> dict[str, Any]:
    """Load the required QM9 subset configuration."""
    if not config_path.is_file():
        raise FileNotFoundError(
            f"Dataset configuration was not found: {config_path}"
        )

    with config_path.open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    required_sections = {"source", "subset", "output"}
    if not isinstance(config, dict):
        raise ValueError("Dataset configuration must contain a YAML mapping.")

    missing_sections = required_sections.difference(config)
    if missing_sections:
        missing = ", ".join(sorted(missing_sections))
        raise ValueError(
            f"Dataset configuration is missing required sections: {missing}"
        )

    return config
