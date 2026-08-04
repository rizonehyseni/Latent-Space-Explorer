"""Run reproducible QM9 robustness experiments."""

import argparse
from pathlib import Path
from typing import Any

from backend.config import load_experiment_config


REQUIRED_CONFIG_SECTIONS = {
    "seeds",
    "data",
    "model",
    "training",
    "evaluation",
    "threshold_selection",
    "artifacts",
}


def parse_arguments() -> argparse.Namespace:
    """Read the robustness configuration path."""
    parser = argparse.ArgumentParser(
        description="Run QM9 robustness experiments."
    )
    parser.add_argument(
        "--config",
        default="configs/qm9_robustness.yaml",
        help="Path to the robustness YAML configuration.",
    )
    return parser.parse_args()


def create_experiment_grid(
    config: dict[str, Any],
) -> list[dict[str, int]]:
    """Create deterministic seed and latent-dimension combinations."""
    seeds = [int(seed) for seed in config["seeds"]]
    latent_dimensions = [
        int(dimension)
        for dimension in config["model"]["latent_dimensions"]
    ]

    if not seeds:
        raise ValueError("At least one seed is required.")

    if not latent_dimensions:
        raise ValueError("At least one latent dimension is required.")

    if len(seeds) != len(set(seeds)):
        raise ValueError("Seeds must be unique.")

    if len(latent_dimensions) != len(set(latent_dimensions)):
        raise ValueError("Latent dimensions must be unique.")

    if any(dimension <= 0 for dimension in latent_dimensions):
        raise ValueError("Latent dimensions must be positive.")

    return [
        {
            "seed": seed,
            "latent_dim": latent_dimension,
        }
        for latent_dimension in latent_dimensions
        for seed in seeds
    ]


def load_robustness_config(
    config_path: Path,
) -> dict[str, Any]:
    """Load and validate the robustness configuration."""
    return load_experiment_config(
        config_path=config_path,
        required_sections=REQUIRED_CONFIG_SECTIONS,
    )


def create_run_name(seed: int, latent_dim: int) -> str:
    """Create a stable identifier for one robustness run."""
    return f"latent_{latent_dim}_seed_{seed}"


def resolve_run_paths(
    project_root: Path,
    artifact_config: dict[str, Any],
    run: dict[str, int],
) -> dict[str, Path]:
    """Resolve checkpoint and result paths for one run."""
    run_name = create_run_name(
        seed=run["seed"],
        latent_dim=run["latent_dim"],
    )

    checkpoint_directory = (
        project_root / artifact_config["checkpoint_directory"]
    )
    results_directory = (
        project_root / artifact_config["run_results_directory"]
    )

    return {
        "checkpoint": checkpoint_directory / f"{run_name}.pt",
        "results": results_directory / f"{run_name}.json",
    }

def main() -> None:
    """Validate and display the planned experiment grid."""
    arguments = parse_arguments()
    project_root = Path(__file__).resolve().parent.parent

    config_path = Path(arguments.config)
    if not config_path.is_absolute():
        config_path = project_root / config_path

    config = load_robustness_config(config_path)
    experiment_grid = create_experiment_grid(config)

    print(f"Experiment: {config['experiment_name']}")
    print(f"Planned runs: {len(experiment_grid)}")

    for run_number, run in enumerate(experiment_grid, start=1):
        print(
            f"Run {run_number:02d}: "
            f"latent_dim={run['latent_dim']}, "
            f"seed={run['seed']}"
        )


if __name__ == "__main__":
    main()