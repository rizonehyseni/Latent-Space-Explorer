"""Run reproducible QM9 robustness experiments."""

import argparse
from pathlib import Path
from typing import Any
import matplotlib.pyplot as plt
import numpy as np
import json
import torch
from torch.utils.data import DataLoader, Subset
from backend.dataset import FingerprintDataset
from backend.model import MolecularVAE
from backend.run_training import load_split_indices
from backend.training import evaluate_vae, train_vae

from backend.config import load_experiment_config
from backend.evaluate_fingerprint_reconstruction import (
    calculate_binary_cross_entropy,
    calculate_prediction_metrics,
    reconstruct_probabilities,
    select_validation_threshold,
)

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
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute training instead of only displaying the grid.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Repeat runs even when their artifacts already exist.",
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


def train_robustness_run(
    project_root: Path,
    config: dict[str, Any],
    run: dict[str, int],
    force: bool = False,
) -> dict[str, Any]:
    """Train and evaluate one seed and latent-dimension combination."""
    seed = run["seed"]
    latent_dim = run["latent_dim"]
    run_name = create_run_name(seed=seed, latent_dim=latent_dim)
    paths = resolve_run_paths(
        project_root=project_root,
        artifact_config=config["artifacts"],
        run=run,
    )

    if (
        not force
        and paths["checkpoint"].is_file()
        and paths["results"].is_file()
    ):
        print(f"Skipping completed run: {run_name}")
        return json.loads(
            paths["results"].read_text(encoding="utf-8")
        )

    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    data_config = config["data"]
    model_config = config["model"]
    training_config = config["training"]

    fingerprint_path = (
        project_root / data_config["fingerprint_path"]
    )
    split_indices_path = (
        project_root / data_config["split_indices_path"]
    )

    dataset = FingerprintDataset(fingerprint_path)
    split_indices = load_split_indices(
        split_path=split_indices_path,
        dataset_size=len(dataset),
    )

    train_dataset = Subset(
        dataset,
        split_indices["train"].tolist(),
    )
    validation_dataset = Subset(
        dataset,
        split_indices["validation"].tolist(),
    )
    test_dataset = Subset(
        dataset,
        split_indices["test"].tolist(),
    )

    batch_size = int(training_config["batch_size"])
    training_generator = torch.Generator().manual_seed(seed)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        generator=training_generator,
    )
    validation_loader = DataLoader(
        validation_dataset,
        batch_size=batch_size,
        shuffle=False,
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
    )

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    run_model_config = {
        "input_dim": int(model_config["input_dim"]),
        "hidden_dim": int(model_config["hidden_dim"]),
        "latent_dim": latent_dim,
    }

    model = MolecularVAE(**run_model_config)
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=float(training_config["learning_rate"]),
    )

    print()
    print(f"Starting run: {run_name}")
    print(f"Device: {device}")

    training_result = train_vae(
        model=model,
        data_loader=train_loader,
        optimizer=optimizer,
        device=device,
        epochs=int(training_config["epochs"]),
        validation_data_loader=validation_loader,
    )

    model.load_state_dict(
        training_result["best_model_state_dict"]
    )
    model.to(device)

    test_metrics = evaluate_vae(
        model=model,
        data_loader=test_loader,
        device=device,
    )

    fingerprints = np.load(fingerprint_path).astype(
        np.float32,
        copy=False,
    )

    evaluation_config = config["evaluation"]
    validation_split = str(
        evaluation_config["validation_split"]
    )
    test_split = str(evaluation_config["test_split"])

    validation_fingerprints = fingerprints[
        split_indices[validation_split]
    ]
    test_fingerprints = fingerprints[
        split_indices[test_split]
    ]

    evaluation_batch_size = int(
        evaluation_config["batch_size"]
    )

    validation_probabilities = reconstruct_probabilities(
        model=model,
        fingerprints=validation_fingerprints,
        batch_size=evaluation_batch_size,
        device=device,
    )
    test_probabilities = reconstruct_probabilities(
        model=model,
        fingerprints=test_fingerprints,
        batch_size=evaluation_batch_size,
        device=device,
    )

    (
        selected_threshold,
        selected_validation_metrics,
        threshold_sweep,
    ) = select_validation_threshold(
        true_fingerprints=validation_fingerprints,
        probabilities=validation_probabilities,
        threshold_config=config["threshold_selection"],
    )

    reconstruction_metrics, _ = calculate_prediction_metrics(
        true_fingerprints=test_fingerprints,
        predicted_fingerprints=(
            test_probabilities >= selected_threshold
        ),
    )
    reconstruction_metrics["mean_binary_cross_entropy"] = float(
        calculate_binary_cross_entropy(
            true_fingerprints=test_fingerprints,
            probabilities=test_probabilities,
        ).mean()
    )

    reference_threshold = float(
        evaluation_config["reference_threshold"]
    )
    reference_metrics, _ = calculate_prediction_metrics(
        true_fingerprints=test_fingerprints,
        predicted_fingerprints=(
            test_probabilities >= reference_threshold
        ),
    )

    reconstruction_evaluation = {
        "selected_threshold": selected_threshold,
        "selection_split": validation_split,
        "selection_metric": config[
            "threshold_selection"
        ]["metric"],
        "selected_validation_metrics": (
            selected_validation_metrics
        ),
        "threshold_sweep": threshold_sweep,
        "test_metrics": reconstruction_metrics,
        "reference_threshold": reference_threshold,
        "reference_test_metrics": reference_metrics,
    }



    checkpoint = {
        "model_state_dict": model.state_dict(),
        "experiment_name": config["experiment_name"],
        "model_config": run_model_config,
        "training_config": training_config,
        "seed": seed,
        "best_epoch": training_result["best_epoch"],
        "best_validation_loss": (
            training_result["best_validation_loss"]
        ),
        "test_metrics": test_metrics,
        "training_history": training_result["history"],
        "reconstruction_evaluation": reconstruction_evaluation
    }

    results = {
        "run_name": run_name,
        "seed": seed,
        "latent_dim": latent_dim,
        "best_epoch": training_result["best_epoch"],
        "best_validation_loss": (
            training_result["best_validation_loss"]
        ),
        "test_metrics": test_metrics,
        "training_history": training_result["history"],
        "reconstruction_evaluation": reconstruction_evaluation
    }

    paths["checkpoint"].parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    paths["results"].parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    torch.save(checkpoint, paths["checkpoint"])
    paths["results"].write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )

    print(f"Completed run: {run_name}")
    print(
        f"Test loss: {test_metrics['loss']:.4f}"
    )
    print(
        "Reconstruction | "
        f"threshold={selected_threshold:.3f} | "
        f"F1={reconstruction_metrics['f1_score']:.4f} | "
        "Mean Tanimoto="
        f"{reconstruction_metrics['mean_tanimoto']:.4f}"
    )

    return results

def summarize_values(
    values: list[float],
) -> dict[str, float]:
    """Summarize repeated experimental measurements."""
    array = np.asarray(values, dtype=np.float64)

    if array.size == 0:
        raise ValueError("Cannot summarize an empty metric list.")

    return {
        "mean": float(array.mean()),
        "standard_deviation": float(
            array.std(ddof=1) if array.size > 1 else 0.0
        ),
        "minimum": float(array.min()),
        "maximum": float(array.max()),
    }


def create_robustness_summary(
    results: list[dict[str, Any]],
    config: dict[str, Any],
) -> dict[str, Any]:
    """Aggregate results by latent dimension."""
    if not results:
        raise ValueError("At least one completed run is required.")

    latent_dimensions = sorted(
        {int(result["latent_dim"]) for result in results}
    )

    aggregate_by_latent_dimension: dict[str, Any] = {}

    for latent_dim in latent_dimensions:
        dimension_results = [
            result
            for result in results
            if int(result["latent_dim"]) == latent_dim
        ]

        aggregate_by_latent_dimension[str(latent_dim)] = {
            "run_count": len(dimension_results),
            "test_loss": summarize_values(
                [
                    float(result["test_metrics"]["loss"])
                    for result in dimension_results
                ]
            ),
            "selected_threshold": summarize_values(
                [
                    float(
                        result["reconstruction_evaluation"][
                            "selected_threshold"
                        ]
                    )
                    for result in dimension_results
                ]
            ),
            "f1_score": summarize_values(
                [
                    float(
                        result["reconstruction_evaluation"][
                            "test_metrics"
                        ]["f1_score"]
                    )
                    for result in dimension_results
                ]
            ),
            "mean_tanimoto": summarize_values(
                [
                    float(
                        result["reconstruction_evaluation"][
                            "test_metrics"
                        ]["mean_tanimoto"]
                    )
                    for result in dimension_results
                ]
            ),
        }

    return {
        "analysis": "qm9_fingerprint_vae_robustness",
        "experiment_name": config["experiment_name"],
        "run_count": len(results),
        "seeds": sorted(
            {int(result["seed"]) for result in results}
        ),
        "latent_dimensions": latent_dimensions,
        "aggregate_by_latent_dimension": (
            aggregate_by_latent_dimension
        ),
        "runs": [
            {
                "run_name": result["run_name"],
                "seed": result["seed"],
                "latent_dim": result["latent_dim"],
                "best_epoch": result["best_epoch"],
                "best_validation_loss": result[
                    "best_validation_loss"
                ],
                "test_metrics": result["test_metrics"],
                "reconstruction_evaluation": result[
                    "reconstruction_evaluation"
                ],
            }
            for result in results
        ],
    }

def create_robustness_figure(
    summary: dict[str, Any],
    figure_path: Path,
) -> None:
    """Plot mean performance with variation across seeds."""
    latent_dimensions = summary["latent_dimensions"]
    aggregate = summary["aggregate_by_latent_dimension"]

    figure, axes = plt.subplots(
        1,
        3,
        figsize=(15, 4.5),
    )

    panels = [
        (
            "test_loss",
            "Held-out VAE loss",
            "Loss",
            "#4C78A8",
        ),
        (
            "f1_score",
            "Fingerprint reconstruction F1",
            "F1 score",
            "#F58518",
        ),
        (
            "mean_tanimoto",
            "Mean fingerprint Tanimoto",
            "Mean Tanimoto",
            "#54A24B",
        ),
    ]

    for axis, (
        metric,
        title,
        ylabel,
        color,
    ) in zip(axes, panels):
        means = [
            aggregate[str(dimension)][metric]["mean"]
            for dimension in latent_dimensions
        ]
        deviations = [
            aggregate[str(dimension)][metric][
                "standard_deviation"
            ]
            for dimension in latent_dimensions
        ]

        axis.errorbar(
            latent_dimensions,
            means,
            yerr=deviations,
            marker="o",
            linewidth=2,
            capsize=5,
            color=color,
        )
        axis.set_title(title)
        axis.set_xlabel("Latent dimensions")
        axis.set_ylabel(ylabel)
        axis.set_xticks(latent_dimensions)
        axis.grid(alpha=0.25)

        if metric in {"f1_score", "mean_tanimoto"}:
            axis.set_ylim(0.0, 1.0)

    figure.suptitle(
        "QM9 Fingerprint VAE Robustness Across Three Seeds"
    )
    figure.tight_layout()

    figure_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(
        figure_path,
        dpi=160,
        bbox_inches="tight",
    )
    plt.close(figure)

def main() -> None:
    """Validate the grid and optionally execute all experiments."""
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

    if not arguments.execute:
        print("Preview complete. Add --execute to start training.")
        return

    run_results = [
        train_robustness_run(
            project_root=project_root,
            config=config,
            run=run,
            force=arguments.force,
        )
        for run in experiment_grid
    ]

    summary = create_robustness_summary(
        results=run_results,
        config=config,
    )
    summary_path = (
        project_root / config["artifacts"]["summary_path"]
    )
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    figure_path = (
        project_root / config["artifacts"]["figure_path"]
    )
    create_robustness_figure(
        summary=summary,
        figure_path=figure_path,
    )    


    print()
    print(f"Robustness summary saved to: {summary_path}")
    print(f"Robustness figure saved to: {figure_path}")

if __name__ == "__main__":
    main()

    