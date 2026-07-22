"""Configuration loading for Fingerprint VAE experiments."""

from pathlib import Path
from typing import Any

import yaml


REQUIRED_SECTIONS = {"data", "model", "training", "artifacts"}


def load_experiment_config(config_path: str | Path) -> dict[str, Any]:
    """Load and validate the required sections of an experiment YAML file."""
    path = Path(config_path)
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file was not found: {path}")

    with path.open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    if not isinstance(config, dict):
        raise ValueError("Configuration must contain a YAML mapping.")

    missing_sections = REQUIRED_SECTIONS.difference(config)
    if missing_sections:
        missing = ", ".join(sorted(missing_sections))
        raise ValueError(f"Configuration is missing required sections: {missing}")

    return config
