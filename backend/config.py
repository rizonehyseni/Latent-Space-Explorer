"""Configuration loading for project experiments."""

from collections.abc import Set
from pathlib import Path
from typing import Any

import yaml


REQUIRED_SECTIONS = {"data", "model", "training", "artifacts"}


def load_experiment_config(
    config_path: str | Path,
    required_sectiona: Set[str] | None = None,
) -> dict[str, Any]:
    """Load a YAML configuration and validate its required sections."""
    path = Path(config_path)

    if not path.is_file():
        raise FileNotFoundError(f"Configuration file was not found: {path}")

    with path.open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    if not isinstance(config, dict):
        raise ValueError("Configuration must contain a YAML mapping.")

    sections = REQUIRED_SECTIONS if required_sections is None else required_sections
    missing_sections = sections.difference(config)


    if missing_sections:
        missing = ", ".join(sorted(missing_sections))
        raise ValueError(f"Configuration is missing required sections: {missing}")

    return config
