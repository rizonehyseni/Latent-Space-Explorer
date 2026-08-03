"""Evaluate deterministic fingerprint reconstruction on a held-out split."""

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch

from backend.config import load_experiment_config
from backend.export_latent_vectors import (
    display_project_path,
    load_fingerprints,
    load_metadata,
    load_split_indices,
    resolve_project_path,
)
from backend.model import MolecularVAE


REQUIRED_CONFIG_SECTIONS = {
    "data",
    "model",
    "evaluation",
    "metrics",
    "baseline",
    "visualization",
    "artifacts",
}


def parse_arguments() -> argparse.Namespace:
    """Read the reconstruction-evaluation configuration path."""
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate deterministic QM9 fingerprint reconstruction."
        )
    )
    parser.add_argument(
        "--config",
        default="configs/qm9_fingerprint_reconstruction.yaml",
        help="Path to the reconstruction-evaluation YAML configuration.",
    )
    return parser.parse_args()


def resolve_device(device_name: str) -> torch.device:
    """Resolve and validate the configured Torch device."""
    if device_name == "cuda" and not torch.cuda.is_available():
        raise ValueError(
            "CUDA was requested but is not available."
        )

    return torch.device(device_name)


def load_reconstruction_model(
    checkpoint_path: Path,
    fingerprint_width: int,
    device: torch.device,
) -> tuple[MolecularVAE, dict[str, Any]]:
    """Load the selected Fingerprint VAE checkpoint."""
    if not checkpoint_path.is_file():
        raise FileNotFoundError(
            f"Model checkpoint was not found: {checkpoint_path}"
        )

    checkpoint = torch.load(
        checkpoint_path,
        map_location=device,
        weights_only=False,
    )

    if "model_state_dict" not in checkpoint:
        raise ValueError(
            "Model checkpoint does not contain model_state_dict."
        )

    model_config = checkpoint.get("model_config")

    if not isinstance(model_config, dict):
        raise ValueError(
            "Model checkpoint does not contain model_config."
        )

    input_dim = int(model_config["input_dim"])

    if input_dim != fingerprint_width:
        raise ValueError(
            "Checkpoint input dimension does not match "
            "the fingerprint width."
        )

    model = MolecularVAE(
        input_dim=input_dim,
        hidden_dim=int(model_config["hidden_dim"]),
        latent_dim=int(model_config["latent_dim"]),
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()

    return model, checkpoint


@torch.inference_mode()
def reconstruct_probabilities(
    model: MolecularVAE,
    fingerprints: np.ndarray,
    batch_size: int,
    device: torch.device,
) -> np.ndarray:
    """Reconstruct probabilities using deterministic latent means."""
    if batch_size <= 0:
        raise ValueError("Evaluation batch_size must be positive.")

    probability_batches: list[np.ndarray] = []

    for start_index in range(0, len(fingerprints), batch_size):
        batch = torch.from_numpy(
            fingerprints[start_index:start_index + batch_size]
        ).to(device)

        latent_means, _ = model.encode(batch)
        reconstruction_logits = model.decode(latent_means)
        probabilities = torch.sigmoid(reconstruction_logits)

        probability_batches.append(
            probabilities.cpu().numpy().astype(np.float32)
        )

    if not probability_batches:
        raise ValueError("Cannot reconstruct an empty fingerprint set.")

    reconstructed = np.concatenate(probability_batches, axis=0)

    if not np.isfinite(reconstructed).all():
        raise ValueError(
            "Reconstruction produced non-finite probabilities."
        )

    return reconstructed


def safe_ratio(numerator: int, denominator: int) -> float:
    """Divide integer counts safely."""
    return float(numerator / denominator) if denominator else 0.0


def calculate_prediction_metrics(
    true_fingerprints: np.ndarray,
    predicted_fingerprints: np.ndarray,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    """Calculate aggregate and per-molecule binary metrics."""
    if true_fingerprints.shape != predicted_fingerprints.shape:
        raise ValueError(
            "True and predicted fingerprints must have identical shapes."
        )

    true_bits = true_fingerprints.astype(bool)
    predicted_bits = predicted_fingerprints.astype(bool)

    true_positive = int(
        np.logical_and(true_bits, predicted_bits).sum()
    )
    true_negative = int(
        np.logical_and(~true_bits, ~predicted_bits).sum()
    )
    false_positive = int(
        np.logical_and(~true_bits, predicted_bits).sum()
    )
    false_negative = int(
        np.logical_and(true_bits, ~predicted_bits).sum()
    )

    total_bits = int(true_bits.size)
    precision = safe_ratio(
        true_positive,
        true_positive + false_positive,
    )
    recall = safe_ratio(
        true_positive,
        true_positive + false_negative,
    )
    f1_score = (
        2.0 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    intersections = np.logical_and(
        true_bits,
        predicted_bits,
    ).sum(axis=1)
    unions = np.logical_or(
        true_bits,
        predicted_bits,
    ).sum(axis=1)

    tanimoto = np.divide(
        intersections,
        unions,
        out=np.ones(len(true_bits), dtype=np.float64),
        where=unions != 0,
    )

    per_molecule_true_positive = np.logical_and(
        true_bits,
        predicted_bits,
    ).sum(axis=1)
    per_molecule_false_positive = np.logical_and(
        ~true_bits,
        predicted_bits,
    ).sum(axis=1)
    per_molecule_false_negative = np.logical_and(
        true_bits,
        ~predicted_bits,
    ).sum(axis=1)

    per_molecule_precision = np.divide(
        per_molecule_true_positive,
        per_molecule_true_positive + per_molecule_false_positive,
        out=np.zeros(len(true_bits), dtype=np.float64),
        where=(
            per_molecule_true_positive
            + per_molecule_false_positive
        ) != 0,
    )
    per_molecule_recall = np.divide(
        per_molecule_true_positive,
        per_molecule_true_positive + per_molecule_false_negative,
        out=np.zeros(len(true_bits), dtype=np.float64),
        where=(
            per_molecule_true_positive
            + per_molecule_false_negative
        ) != 0,
    )
    per_molecule_f1 = np.divide(
        2.0 * per_molecule_precision * per_molecule_recall,
        per_molecule_precision + per_molecule_recall,
        out=np.zeros(len(true_bits), dtype=np.float64),
        where=(
            per_molecule_precision + per_molecule_recall
        ) != 0,
    )

    exact_matches = np.all(
        true_bits == predicted_bits,
        axis=1,
    )
    bit_accuracy_by_molecule = np.mean(
        true_bits == predicted_bits,
        axis=1,
    )

    aggregate = {
        "bit_accuracy": safe_ratio(
            true_positive + true_negative,
            total_bits,
        ),
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "exact_match_rate": float(exact_matches.mean()),
        "mean_tanimoto": float(tanimoto.mean()),
        "median_tanimoto": float(np.median(tanimoto)),
        "tanimoto_standard_deviation": float(tanimoto.std()),
        "minimum_tanimoto": float(tanimoto.min()),
        "maximum_tanimoto": float(tanimoto.max()),
        "true_bit_density": float(true_bits.mean()),
        "predicted_bit_density": float(predicted_bits.mean()),
        "confusion_counts": {
            "true_positive": true_positive,
            "true_negative": true_negative,
            "false_positive": false_positive,
            "false_negative": false_negative,
        },
    }

    per_molecule = {
        "true_active_bits": true_bits.sum(axis=1),
        "predicted_active_bits": predicted_bits.sum(axis=1),
        "bit_accuracy": bit_accuracy_by_molecule,
        "precision": per_molecule_precision,
        "recall": per_molecule_recall,
        "f1_score": per_molecule_f1,
        "tanimoto_similarity": tanimoto,
        "exact_match": exact_matches,
    }

    return aggregate, per_molecule


def calculate_binary_cross_entropy(
    true_fingerprints: np.ndarray,
    probabilities: np.ndarray,
) -> np.ndarray:
    """Calculate mean binary cross-entropy for each molecule."""
    epsilon = np.finfo(np.float32).eps
    clipped_probabilities = np.clip(
        probabilities,
        epsilon,
        1.0 - epsilon,
    )

    return -np.mean(
        true_fingerprints * np.log(clipped_probabilities)
        + (1.0 - true_fingerprints)
        * np.log(1.0 - clipped_probabilities),
        axis=1,
    )


def save_metrics_figure(
    model_metrics: dict[str, Any],
    baseline_metrics: dict[str, Any],
    figure_path: Path,
    figure_dpi: int,
) -> None:
    """Save a model-versus-baseline metric comparison."""
    figure_path.parent.mkdir(parents=True, exist_ok=True)

    metric_names = [
        "bit_accuracy",
        "precision",
        "recall",
        "f1_score",
        "mean_tanimoto",
        "exact_match_rate",
    ]
    display_names = [
        "Bit accuracy",
        "Precision",
        "Recall",
        "F1",
        "Mean Tanimoto",
        "Exact match",
    ]

    model_values = [
        float(model_metrics[name])
        for name in metric_names
    ]
    baseline_values = [
        float(baseline_metrics[name])
        for name in metric_names
    ]

    positions = np.arange(len(metric_names))
    width = 0.36

    figure, axis = plt.subplots(figsize=(12, 7), dpi=figure_dpi)
    model_bars = axis.bar(
        positions - width / 2,
        model_values,
        width,
        label="Fingerprint VAE",
        color="#2563eb",
    )
    baseline_bars = axis.bar(
        positions + width / 2,
        baseline_values,
        width,
        label="All-zero baseline",
        color="#94a3b8",
    )

    axis.bar_label(model_bars, fmt="%.3f", padding=3)
    axis.bar_label(baseline_bars, fmt="%.3f", padding=3)
    axis.set_xticks(positions, display_names)
    axis.set_ylim(0.0, 1.08)
    axis.set_ylabel("Metric value")
    axis.set_title(
        "QM9 held-out fingerprint reconstruction quality",
        fontweight="bold",
        pad=14,
    )
    axis.grid(axis="y", alpha=0.2)
    axis.legend(frameon=False)

    figure.tight_layout()
    figure.savefig(figure_path, bbox_inches="tight")
    plt.close(figure)


def save_tanimoto_figure(
    tanimoto_values: np.ndarray,
    figure_path: Path,
    figure_dpi: int,
    histogram_bins: int,
) -> None:
    """Save the per-molecule reconstruction Tanimoto distribution."""
    figure_path.parent.mkdir(parents=True, exist_ok=True)

    mean_value = float(tanimoto_values.mean())
    median_value = float(np.median(tanimoto_values))

    figure, axis = plt.subplots(figsize=(10, 7), dpi=figure_dpi)
    axis.hist(
        tanimoto_values,
        bins=histogram_bins,
        range=(0.0, 1.0),
        color="#2563eb",
        alpha=0.8,
        edgecolor="white",
    )
    axis.axvline(
        mean_value,
        color="#dc2626",
        linestyle="--",
        linewidth=2,
        label=f"Mean: {mean_value:.3f}",
    )
    axis.axvline(
        median_value,
        color="#f59e0b",
        linestyle="--",
        linewidth=2,
        label=f"Median: {median_value:.3f}",
    )

    axis.set_xlim(0.0, 1.0)
    axis.set_xlabel(
        "Original-versus-reconstructed Tanimoto similarity"
    )
    axis.set_ylabel("Test molecules")
    axis.set_title(
        "QM9 fingerprint reconstruction similarity",
        fontweight="bold",
        pad=14,
    )
    axis.grid(axis="y", alpha=0.2)
    axis.legend(frameon=False)

    figure.tight_layout()
    figure.savefig(figure_path, bbox_inches="tight")
    plt.close(figure)


def create_reconstruction_artifacts(
    fingerprints_path: Path,
    metadata_path: Path,
    split_indices_path: Path,
    checkpoint_path: Path,
    per_molecule_path: Path,
    summary_path: Path,
    metrics_figure_path: Path,
    tanimoto_figure_path: Path,
    evaluation_config: dict[str, Any],
    metrics_config: dict[str, Any],
    baseline_config: dict[str, Any],
    visualization_config: dict[str, Any],
    project_root: Path,
) -> dict[str, Any]:
    """Evaluate reconstruction and write aligned artifacts."""
    fingerprints = load_fingerprints(fingerprints_path)

    if not np.isfinite(fingerprints).all():
        raise ValueError("Fingerprints contain non-finite values.")

    if not np.isin(np.unique(fingerprints), [0.0, 1.0]).all():
        raise ValueError("Fingerprints must contain only binary values.")

    metadata = load_metadata(
        metadata_path,
        dataset_size=len(fingerprints),
    )
    split_indices = load_split_indices(
        split_path=split_indices_path,
        dataset_size=len(fingerprints),
    )

    evaluation_split = str(evaluation_config["split"])

    if evaluation_split not in split_indices:
        raise ValueError(
            f"Unknown evaluation split: {evaluation_split}"
        )

    evaluation_indices = split_indices[evaluation_split]
    evaluation_fingerprints = fingerprints[evaluation_indices]

    threshold = float(
        evaluation_config["probability_threshold"]
    )

    if not 0.0 < threshold < 1.0:
        raise ValueError(
            "probability_threshold must be between 0 and 1."
        )

    device = resolve_device(str(evaluation_config.get("device", "cpu")))
    model, checkpoint = load_reconstruction_model(
        checkpoint_path=checkpoint_path,
        fingerprint_width=fingerprints.shape[1],
        device=device,
    )

    probabilities = reconstruct_probabilities(
        model=model,
        fingerprints=evaluation_fingerprints,
        batch_size=int(evaluation_config["batch_size"]),
        device=device,
    )
    predicted_fingerprints = probabilities >= threshold

    model_metrics, per_molecule_metrics = (
        calculate_prediction_metrics(
            true_fingerprints=evaluation_fingerprints,
            predicted_fingerprints=predicted_fingerprints,
        )
    )

    binary_cross_entropy = calculate_binary_cross_entropy(
        true_fingerprints=evaluation_fingerprints,
        probabilities=probabilities,
    )
    model_metrics["mean_binary_cross_entropy"] = float(
        binary_cross_entropy.mean()
    )

    if not baseline_config.get("all_zero_fingerprint", False):
        raise ValueError(
            "The all-zero baseline must be enabled."
        )

    all_zero_predictions = np.zeros_like(
        evaluation_fingerprints,
        dtype=bool,
    )
    baseline_metrics, _ = calculate_prediction_metrics(
        true_fingerprints=evaluation_fingerprints,
        predicted_fingerprints=all_zero_predictions,
    )

    selected_metadata = metadata.iloc[
        evaluation_indices
    ].reset_index(drop=True)

    per_molecule = pd.DataFrame(
        {
            "dataset_index": evaluation_indices,
            "source_index": selected_metadata["source_index"],
            "id": selected_metadata["id"],
            "smiles": selected_metadata["smiles"],
            "split": evaluation_split,
            **per_molecule_metrics,
            "binary_cross_entropy": binary_cross_entropy,
        }
    )

    per_molecule_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    per_molecule.to_csv(per_molecule_path, index=False)

    save_metrics_figure(
        model_metrics=model_metrics,
        baseline_metrics=baseline_metrics,
        figure_path=metrics_figure_path,
        figure_dpi=int(visualization_config["figure_dpi"]),
    )
    save_tanimoto_figure(
        tanimoto_values=per_molecule_metrics[
            "tanimoto_similarity"
        ],
        figure_path=tanimoto_figure_path,
        figure_dpi=int(visualization_config["figure_dpi"]),
        histogram_bins=int(
            visualization_config["histogram_bins"]
        ),
    )

    summary = {
        "artifact_schema_version": 1,
        "analysis": "fingerprint_reconstruction_evaluation",
        "evaluation_split": evaluation_split,
        "evaluation_molecules": len(evaluation_indices),
        "probability_threshold": threshold,
        "deterministic_latent": evaluation_config[
            "deterministic_latent"
        ],
        "model_metrics": model_metrics,
        "all_zero_baseline": baseline_metrics,
        "requested_metrics": metrics_config,
        "checkpoint": {
            "path": display_project_path(
                project_root,
                checkpoint_path,
            ),
            "experiment_name": checkpoint.get("experiment_name"),
            "best_epoch": checkpoint.get("best_epoch"),
            "best_validation_loss": checkpoint.get(
                "best_validation_loss"
            ),
            "model_config": checkpoint.get("model_config"),
        },
        "inputs": {
            "fingerprints_path": display_project_path(
                project_root,
                fingerprints_path,
            ),
            "metadata_path": display_project_path(
                project_root,
                metadata_path,
            ),
            "split_indices_path": display_project_path(
                project_root,
                split_indices_path,
            ),
        },
        "outputs": {
            "per_molecule_path": display_project_path(
                project_root,
                per_molecule_path,
            ),
            "metrics_figure_path": display_project_path(
                project_root,
                metrics_figure_path,
            ),
            "tanimoto_figure_path": display_project_path(
                project_root,
                tanimoto_figure_path,
            ),
        },
    }

    summary_path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    return summary


def main() -> None:
    """Run the configured reconstruction evaluation."""
    arguments = parse_arguments()
    project_root = Path(__file__).resolve().parent.parent
    config_path = Path(arguments.config)

    if not config_path.is_absolute():
        config_path = project_root / config_path

    config = load_experiment_config(
        config_path,
        required_sections=REQUIRED_CONFIG_SECTIONS,
    )

    data_config = config["data"]
    model_config = config["model"]
    artifact_config = config["artifacts"]
    evaluation_config = {
        **config["evaluation"],
        "device": model_config["device"],
        "deterministic_latent": model_config[
            "deterministic_latent"
        ],
    }

    summary = create_reconstruction_artifacts(
        fingerprints_path=resolve_project_path(
            project_root,
            data_config["fingerprints_path"],
        ),
        metadata_path=resolve_project_path(
            project_root,
            data_config["metadata_path"],
        ),
        split_indices_path=resolve_project_path(
            project_root,
            data_config["split_indices_path"],
        ),
        checkpoint_path=resolve_project_path(
            project_root,
            model_config["checkpoint_path"],
        ),
        per_molecule_path=resolve_project_path(
            project_root,
            artifact_config["per_molecule_path"],
        ),
        summary_path=resolve_project_path(
            project_root,
            artifact_config["summary_path"],
        ),
        metrics_figure_path=resolve_project_path(
            project_root,
            artifact_config["metrics_figure_path"],
        ),
        tanimoto_figure_path=resolve_project_path(
            project_root,
            artifact_config["tanimoto_figure_path"],
        ),
        evaluation_config=evaluation_config,
        metrics_config=config["metrics"],
        baseline_config=config["baseline"],
        visualization_config=config["visualization"],
        project_root=project_root,
    )

    metrics = summary["model_metrics"]
    baseline = summary["all_zero_baseline"]

    print(f"Evaluation molecules: {summary['evaluation_molecules']}")
    print(f"Probability threshold: {summary['probability_threshold']}")
    print(f"Bit accuracy: {metrics['bit_accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall: {metrics['recall']:.4f}")
    print(f"F1 score: {metrics['f1_score']:.4f}")
    print(f"Mean Tanimoto: {metrics['mean_tanimoto']:.4f}")
    print(
        "All-zero baseline accuracy: "
        f"{baseline['bit_accuracy']:.4f}"
    )


if __name__ == "__main__":
    main()