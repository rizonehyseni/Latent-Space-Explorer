"""Generate reproducible training curves from a saved VAE results artifact."""

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


METRIC_PAIRS = (
    (
        "loss",
        "validation_loss",
        "Total VAE loss",
    ),
    (
        "reconstruction_loss",
        "validation_reconstruction_loss",
        "Reconstruction loss",
    ),
    (
        "kl_divergence",
        "validation_kl_divergence",
        "KL divergence",
    ),
)


def parse_arguments() -> argparse.Namespace:
    """Read the results artifact and output figure paths."""
    parser = argparse.ArgumentParser(
        description="Generate Fingerprint VAE training curves."
    )
    parser.add_argument(
        "--results",
        default="models/qm9_fingerprint_vae_results.json",
        help="Path to the generated QM9 evaluation results JSON file.",
    )
    parser.add_argument(
        "--output",
        default=(
            "docs/FIGURES/"
            "qm9-fingerprint-vae-training-curves-v1.png"
        ),
        help="Path for the generated PNG figure.",
    )
    return parser.parse_args()


def load_training_history(results_path: Path) -> list[dict[str, Any]]:
    """Load and validate the stored training history."""
    if not results_path.is_file():
        raise FileNotFoundError(
            f"Training results file was not found: {results_path}"
        )

    with results_path.open(encoding="utf-8") as results_file:
        results = json.load(results_file)

    history = results.get("training_history")

    if not isinstance(history, list) or not history:
        raise ValueError(
            "Results JSON must contain a non-empty training_history list."
        )

    required_metrics = {
        "epoch",
        *(metric for pair in METRIC_PAIRS for metric in pair[:2]),
    }

    for epoch_metrics in history:
        missing_metrics = required_metrics.difference(epoch_metrics)

        if missing_metrics:
            missing = ", ".join(sorted(missing_metrics))
            raise ValueError(
                f"Training history is missing required metrics: {missing}"
            )

    return history


def plot_training_history(
    history: list[dict[str, Any]],
    output_path: Path,
) -> None:
    """Create a three-panel training and validation loss figure."""
    epochs = [entry["epoch"] for entry in history]

    figure, axes = plt.subplots(
        nrows=1,
        ncols=3,
        figsize=(15, 4.8),
        constrained_layout=True,
    )

    for axis, (training_key, validation_key, title) in zip(
        axes,
        METRIC_PAIRS,
        strict=True,
    ):
        training_values = [entry[training_key] for entry in history]
        validation_values = [entry[validation_key] for entry in history]

        axis.plot(
            epochs,
            training_values,
            color="#4C78A8",
            linewidth=2,
            label="Training",
        )
        axis.plot(
            epochs,
            validation_values,
            color="#F58518",
            linewidth=2,
            label="Validation",
        )

        axis.set_title(title)
        axis.set_xlabel("Epoch")
        axis.set_ylabel("Per-sample loss")
        axis.grid(alpha=0.25)
        axis.legend(frameon=False)

    figure.suptitle(
        "QM9 Fingerprint VAE baseline training history",
        fontsize=14,
        fontweight="bold",
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(
        output_path,
        dpi=220,
        bbox_inches="tight",
    )
    plt.close(figure)


def main() -> None:
    """Load saved results and generate the training-curve figure."""
    arguments = parse_arguments()
    project_root = Path(__file__).resolve().parent.parent

    results_path = Path(arguments.results)
    if not results_path.is_absolute():
        results_path = project_root / results_path

    output_path = Path(arguments.output)
    if not output_path.is_absolute():
        output_path = project_root / output_path

    history = load_training_history(results_path)
    plot_training_history(history, output_path)

    print(f"Training curve figure saved to: {output_path}")


if __name__ == "__main__":
    main()