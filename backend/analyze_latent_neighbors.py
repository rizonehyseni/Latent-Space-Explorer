"""Evaluate latent nearest neighbors with fingerprint Tanimoto similarity."""

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

from backend.config import load_experiment_config
from backend.plot_latent_pca import (
    display_project_path,
    load_export_manifest,
    resolve_project_path,
)


REQUIRED_CONFIG_SECTIONS = {
    "data",
    "analysis",
    "fingerprint",
    "visualization",
    "artifacts",
}
REQUIRED_METADATA_COLUMNS = {
    "latent_row",
    "id",
    "smiles",
    "split",
}


def parse_arguments() -> argparse.Namespace:
    """Read the selected neighbor-analysis configuration."""
    parser = argparse.ArgumentParser(
        description=(
            "Compare latent nearest neighbors with Morgan-fingerprint "
            "Tanimoto similarity."
        )
    )
    parser.add_argument(
        "--config",
        default="configs/qm9_latent_neighbor_tanimoto.yaml",
        help="Path to the neighbor-analysis YAML configuration.",
    )
    return parser.parse_args()


def load_analysis_inputs(
    latent_vectors_path: Path,
    metadata_path: Path,
    fingerprints_path: Path,
    expected_fingerprint_bits: int,
) -> tuple[np.ndarray, pd.DataFrame, np.ndarray]:
    """Load and validate aligned latent, metadata, and fingerprint data."""
    if not latent_vectors_path.is_file():
        raise FileNotFoundError(
            f"Latent vectors were not found: {latent_vectors_path}"
        )

    if not metadata_path.is_file():
        raise FileNotFoundError(
            f"Latent metadata was not found: {metadata_path}"
        )

    if not fingerprints_path.is_file():
        raise FileNotFoundError(
            f"Fingerprint data was not found: {fingerprints_path}"
        )

    latent_vectors = np.load(latent_vectors_path)
    fingerprints = np.load(fingerprints_path)
    metadata = pd.read_csv(metadata_path)

    if latent_vectors.ndim != 2:
        raise ValueError("Latent vectors must be a two-dimensional matrix.")

    if fingerprints.ndim != 2:
        raise ValueError("Fingerprints must be a two-dimensional matrix.")

    if latent_vectors.shape[0] == 0:
        raise ValueError("Latent-vector data cannot be empty.")

    dataset_size = latent_vectors.shape[0]

    if len(metadata) != dataset_size:
        raise ValueError(
            "Metadata row count must match the latent-vector count."
        )

    if fingerprints.shape[0] != dataset_size:
        raise ValueError(
            "Fingerprint row count must match the latent-vector count."
        )

    if fingerprints.shape[1] != expected_fingerprint_bits:
        raise ValueError(
            "Fingerprint width does not match the configured bit count."
        )

    missing_columns = REQUIRED_METADATA_COLUMNS.difference(
        metadata.columns
    )

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"Latent metadata is missing required columns: {missing}"
        )

    expected_rows = np.arange(dataset_size)

    if not np.array_equal(
        metadata["latent_row"].to_numpy(),
        expected_rows,
    ):
        raise ValueError(
            "latent_row must be sequential and aligned with artifact rows."
        )

    if metadata["latent_row"].duplicated().any():
        raise ValueError("Metadata contains duplicate latent rows.")

    if metadata["id"].duplicated().any():
        raise ValueError("Metadata contains duplicate molecule IDs.")

    if not np.isfinite(latent_vectors).all():
        raise ValueError("Latent vectors contain non-finite values.")

    if not np.isfinite(fingerprints).all():
        raise ValueError("Fingerprints contain non-finite values.")

    unique_fingerprint_values = np.unique(fingerprints)

    if not np.isin(unique_fingerprint_values, [0.0, 1.0]).all():
        raise ValueError("Fingerprints must contain only binary values.")

    return (
        latent_vectors.astype(np.float32),
        metadata,
        fingerprints.astype(bool),
    )


def calculate_tanimoto_similarities(
    query_fingerprint: np.ndarray,
    candidate_fingerprints: np.ndarray,
) -> np.ndarray:
    """Calculate Tanimoto similarity for one query and many candidates."""
    intersections = np.logical_and(
        candidate_fingerprints,
        query_fingerprint,
    ).sum(axis=1)

    unions = np.logical_or(
        candidate_fingerprints,
        query_fingerprint,
    ).sum(axis=1)

    return np.divide(
        intersections,
        unions,
        out=np.ones(len(candidate_fingerprints), dtype=np.float64),
        where=unions != 0,
    )


def calculate_correlation(
    first_values: np.ndarray,
    second_values: np.ndarray,
) -> float | None:
    """Calculate Pearson correlation when both arrays vary."""
    if np.std(first_values) == 0 or np.std(second_values) == 0:
        return None

    return float(np.corrcoef(first_values, second_values)[0, 1])


def calculate_spearman_correlation(
    first_values: np.ndarray,
    second_values: np.ndarray,
) -> float | None:
    """Calculate Spearman correlation using average ranks."""
    first_ranks = pd.Series(first_values).rank(
        method="average"
    ).to_numpy()
    second_ranks = pd.Series(second_values).rank(
        method="average"
    ).to_numpy()

    return calculate_correlation(first_ranks, second_ranks)


def run_neighbor_analysis(
    latent_vectors: np.ndarray,
    metadata: pd.DataFrame,
    fingerprints: np.ndarray,
    query_split: str,
    reference_split: str,
    distance_metric: str,
    neighbors_per_query: int,
    random_neighbors_per_query: int,
    random_seed: int,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Find latent neighbors and compare them with a random baseline."""
    if query_split == reference_split:
        raise ValueError(
            "Query and reference splits must be different."
        )

    if neighbors_per_query <= 0:
        raise ValueError("neighbors_per_query must be positive.")

    if random_neighbors_per_query != neighbors_per_query:
        raise ValueError(
            "random_neighbors_per_query must equal "
            "neighbors_per_query for paired comparisons."
        )

    split_values = metadata["split"].to_numpy()
    query_indices = np.flatnonzero(split_values == query_split)
    reference_indices = np.flatnonzero(
        split_values == reference_split
    )

    if len(query_indices) == 0:
        raise ValueError(
            f"No molecules were found in query split '{query_split}'."
        )

    if len(reference_indices) == 0:
        raise ValueError(
            f"No molecules were found in reference split "
            f"'{reference_split}'."
        )

    if neighbors_per_query > len(reference_indices):
        raise ValueError(
            "neighbors_per_query cannot exceed the reference-set size."
        )

    nearest_neighbor_model = NearestNeighbors(
        n_neighbors=neighbors_per_query,
        metric=distance_metric,
        algorithm="brute",
        n_jobs=1,
    )
    nearest_neighbor_model.fit(latent_vectors[reference_indices])

    neighbor_distances, neighbor_local_indices = (
        nearest_neighbor_model.kneighbors(
            latent_vectors[query_indices],
            return_distance=True,
        )
    )

    random_generator = np.random.default_rng(random_seed)
    records: list[dict[str, Any]] = []
    nearest_similarity_rows: list[np.ndarray] = []
    random_similarity_rows: list[np.ndarray] = []

    molecule_ids = metadata["id"].to_numpy()
    smiles_values = metadata["smiles"].to_numpy()
    latent_rows = metadata["latent_row"].to_numpy()

    for query_position, query_global_index in enumerate(query_indices):
        nearest_global_indices = reference_indices[
            neighbor_local_indices[query_position]
        ]
        random_global_indices = random_generator.choice(
            reference_indices,
            size=random_neighbors_per_query,
            replace=False,
        )

        query_fingerprint = fingerprints[query_global_index]
        nearest_similarities = calculate_tanimoto_similarities(
            query_fingerprint,
            fingerprints[nearest_global_indices],
        )
        random_similarities = calculate_tanimoto_similarities(
            query_fingerprint,
            fingerprints[random_global_indices],
        )

        nearest_similarity_rows.append(nearest_similarities)
        random_similarity_rows.append(random_similarities)

        for rank in range(neighbors_per_query):
            neighbor_global_index = nearest_global_indices[rank]
            random_global_index = random_global_indices[rank]

            records.append(
                {
                    "query_latent_row": int(
                        latent_rows[query_global_index]
                    ),
                    "query_id": str(
                        molecule_ids[query_global_index]
                    ),
                    "query_smiles": str(
                        smiles_values[query_global_index]
                    ),
                    "query_split": query_split,
                    "neighbor_rank": rank + 1,
                    "neighbor_latent_row": int(
                        latent_rows[neighbor_global_index]
                    ),
                    "neighbor_id": str(
                        molecule_ids[neighbor_global_index]
                    ),
                    "neighbor_smiles": str(
                        smiles_values[neighbor_global_index]
                    ),
                    "reference_split": reference_split,
                    "latent_distance": float(
                        neighbor_distances[query_position, rank]
                    ),
                    "tanimoto_similarity": float(
                        nearest_similarities[rank]
                    ),
                    "random_reference_latent_row": int(
                        latent_rows[random_global_index]
                    ),
                    "random_reference_id": str(
                        molecule_ids[random_global_index]
                    ),
                    "random_reference_smiles": str(
                        smiles_values[random_global_index]
                    ),
                    "random_tanimoto_similarity": float(
                        random_similarities[rank]
                    ),
                }
            )

    results = pd.DataFrame.from_records(records)
    nearest_matrix = np.vstack(nearest_similarity_rows)
    random_matrix = np.vstack(random_similarity_rows)
    flattened_distances = neighbor_distances.reshape(-1)
    flattened_nearest = nearest_matrix.reshape(-1)
    flattened_random = random_matrix.reshape(-1)

    pearson_correlation = calculate_correlation(
        flattened_distances,
        flattened_nearest,
    )
    spearman_correlation = calculate_spearman_correlation(
        flattened_distances,
        flattened_nearest,
    )

    summary = {
        "query_split": query_split,
        "reference_split": reference_split,
        "query_count": len(query_indices),
        "reference_count": len(reference_indices),
        "neighbors_per_query": neighbors_per_query,
        "comparison_count": len(flattened_nearest),
        "latent_distance_metric": distance_metric,
        "nearest_neighbor_tanimoto": {
            "mean": float(flattened_nearest.mean()),
            "median": float(np.median(flattened_nearest)),
            "standard_deviation": float(flattened_nearest.std()),
            "minimum": float(flattened_nearest.min()),
            "maximum": float(flattened_nearest.max()),
        },
        "random_baseline_tanimoto": {
            "mean": float(flattened_random.mean()),
            "median": float(np.median(flattened_random)),
            "standard_deviation": float(flattened_random.std()),
            "minimum": float(flattened_random.min()),
            "maximum": float(flattened_random.max()),
        },
        "mean_tanimoto_improvement": float(
            flattened_nearest.mean() - flattened_random.mean()
        ),
        "nearest_beats_paired_random_fraction": float(
            np.mean(flattened_nearest > flattened_random)
        ),
        "latent_distance_tanimoto_pearson": pearson_correlation,
        "latent_distance_tanimoto_spearman": spearman_correlation,
        "mean_tanimoto_by_rank": {
            str(rank + 1): float(nearest_matrix[:, rank].mean())
            for rank in range(neighbors_per_query)
        },
    }

    return results, summary


def save_distance_similarity_figure(
    results: pd.DataFrame,
    summary: dict[str, Any],
    figure_path: Path,
    figure_dpi: int,
    point_alpha: float,
) -> None:
    """Plot latent distance against Tanimoto similarity."""
    figure_path.parent.mkdir(parents=True, exist_ok=True)

    figure, axis = plt.subplots(figsize=(10, 8), dpi=figure_dpi)
    axis.scatter(
        results["latent_distance"],
        results["tanimoto_similarity"],
        s=10,
        alpha=point_alpha,
        color="#2563eb",
        edgecolors="none",
        rasterized=True,
    )

    pearson = summary["latent_distance_tanimoto_pearson"]
    spearman = summary["latent_distance_tanimoto_spearman"]

    axis.set_title(
        "QM9 latent distance vs. fingerprint similarity",
        fontweight="bold",
        pad=14,
    )
    axis.set_xlabel("Euclidean distance in 16D latent space")
    axis.set_ylabel("Morgan-fingerprint Tanimoto similarity")
    axis.set_ylim(-0.02, 1.02)
    axis.grid(alpha=0.2)

    annotation = (
        f"Pearson: {pearson:.3f}\n"
        f"Spearman: {spearman:.3f}"
    )
    axis.text(
        0.98,
        0.96,
        annotation,
        transform=axis.transAxes,
        ha="right",
        va="top",
        bbox={
            "boxstyle": "round",
            "facecolor": "white",
            "alpha": 0.85,
        },
    )

    figure.tight_layout()
    figure.savefig(figure_path, bbox_inches="tight")
    plt.close(figure)


def save_baseline_figure(
    results: pd.DataFrame,
    summary: dict[str, Any],
    figure_path: Path,
    figure_dpi: int,
    histogram_bins: int,
) -> None:
    """Compare nearest-neighbor and random Tanimoto distributions."""
    figure_path.parent.mkdir(parents=True, exist_ok=True)

    figure, axis = plt.subplots(figsize=(10, 8), dpi=figure_dpi)

    axis.hist(
        results["random_tanimoto_similarity"],
        bins=histogram_bins,
        range=(0.0, 1.0),
        density=True,
        alpha=0.65,
        color="#94a3b8",
        label="Random training molecules",
    )
    axis.hist(
        results["tanimoto_similarity"],
        bins=histogram_bins,
        range=(0.0, 1.0),
        density=True,
        alpha=0.65,
        color="#2563eb",
        label="Latent nearest neighbors",
    )

    nearest_mean = summary["nearest_neighbor_tanimoto"]["mean"]
    random_mean = summary["random_baseline_tanimoto"]["mean"]

    axis.axvline(
        nearest_mean,
        color="#1d4ed8",
        linestyle="--",
        linewidth=2,
        label=f"Nearest mean: {nearest_mean:.3f}",
    )
    axis.axvline(
        random_mean,
        color="#475569",
        linestyle="--",
        linewidth=2,
        label=f"Random mean: {random_mean:.3f}",
    )

    axis.set_title(
        "QM9 latent neighbors vs. random fingerprint similarity",
        fontweight="bold",
        pad=14,
    )
    axis.set_xlabel("Morgan-fingerprint Tanimoto similarity")
    axis.set_ylabel("Density")
    axis.set_xlim(0.0, 1.0)
    axis.grid(alpha=0.2)
    axis.legend(frameon=False)

    figure.tight_layout()
    figure.savefig(figure_path, bbox_inches="tight")
    plt.close(figure)


def create_neighbor_analysis_artifacts(
    latent_vectors_path: Path,
    metadata_path: Path,
    fingerprints_path: Path,
    latent_export_manifest_path: Path,
    neighbors_path: Path,
    summary_path: Path,
    distance_similarity_figure_path: Path,
    baseline_figure_path: Path,
    analysis_config: dict[str, Any],
    fingerprint_config: dict[str, Any],
    visualization_config: dict[str, Any],
    project_root: Path,
) -> dict[str, Any]:
    """Create neighbor results, summary, and scientific figures."""
    latent_vectors, metadata, fingerprints = load_analysis_inputs(
        latent_vectors_path=latent_vectors_path,
        metadata_path=metadata_path,
        fingerprints_path=fingerprints_path,
        expected_fingerprint_bits=int(fingerprint_config["bits"]),
    )
    latent_export_manifest = load_export_manifest(
        latent_export_manifest_path
    )

    results, analysis_summary = run_neighbor_analysis(
        latent_vectors=latent_vectors,
        metadata=metadata,
        fingerprints=fingerprints,
        query_split=str(analysis_config["query_split"]),
        reference_split=str(analysis_config["reference_split"]),
        distance_metric=str(
            analysis_config["latent_distance_metric"]
        ),
        neighbors_per_query=int(
            analysis_config["neighbors_per_query"]
        ),
        random_neighbors_per_query=int(
            analysis_config["random_neighbors_per_query"]
        ),
        random_seed=int(analysis_config["random_seed"]),
    )

    neighbors_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    results.to_csv(neighbors_path, index=False)

    save_distance_similarity_figure(
        results=results,
        summary=analysis_summary,
        figure_path=distance_similarity_figure_path,
        figure_dpi=int(visualization_config["figure_dpi"]),
        point_alpha=float(visualization_config["point_alpha"]),
    )
    save_baseline_figure(
        results=results,
        summary=analysis_summary,
        figure_path=baseline_figure_path,
        figure_dpi=int(visualization_config["figure_dpi"]),
        histogram_bins=int(
            visualization_config["histogram_bins"]
        ),
    )

    summary = {
        "artifact_schema_version": 1,
        "analysis": "latent_neighbor_tanimoto",
        **analysis_summary,
        "fingerprint": fingerprint_config,
        "source_latent_export": {
            "latent_representation": latent_export_manifest.get(
                "latent_representation"
            ),
            "checkpoint": latent_export_manifest.get("checkpoint"),
        },
        "inputs": {
            "latent_vectors_path": display_project_path(
                project_root,
                latent_vectors_path,
            ),
            "metadata_path": display_project_path(
                project_root,
                metadata_path,
            ),
            "fingerprints_path": display_project_path(
                project_root,
                fingerprints_path,
            ),
        },
        "outputs": {
            "neighbors_path": display_project_path(
                project_root,
                neighbors_path,
            ),
            "distance_similarity_figure_path": display_project_path(
                project_root,
                distance_similarity_figure_path,
            ),
            "baseline_figure_path": display_project_path(
                project_root,
                baseline_figure_path,
            ),
        },
    }

    summary_path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    return summary


def main() -> None:
    """Run the configured latent-neighbor analysis."""
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
    artifact_config = config["artifacts"]

    summary = create_neighbor_analysis_artifacts(
        latent_vectors_path=resolve_project_path(
            project_root,
            data_config["latent_vectors_path"],
        ),
        metadata_path=resolve_project_path(
            project_root,
            data_config["latent_metadata_path"],
        ),
        fingerprints_path=resolve_project_path(
            project_root,
            data_config["fingerprints_path"],
        ),
        latent_export_manifest_path=resolve_project_path(
            project_root,
            data_config["latent_export_manifest_path"],
        ),
        neighbors_path=resolve_project_path(
            project_root,
            artifact_config["neighbors_path"],
        ),
        summary_path=resolve_project_path(
            project_root,
            artifact_config["summary_path"],
        ),
        distance_similarity_figure_path=resolve_project_path(
            project_root,
            artifact_config[
                "distance_similarity_figure_path"
            ],
        ),
        baseline_figure_path=resolve_project_path(
            project_root,
            artifact_config["baseline_figure_path"],
        ),
        analysis_config=config["analysis"],
        fingerprint_config=config["fingerprint"],
        visualization_config=config["visualization"],
        project_root=project_root,
    )

    print(f"Queries: {summary['query_count']}")
    print(f"References: {summary['reference_count']}")
    print(
        "Nearest-neighbor mean Tanimoto: "
        f"{summary['nearest_neighbor_tanimoto']['mean']:.4f}"
    )
    print(
        "Random-baseline mean Tanimoto: "
        f"{summary['random_baseline_tanimoto']['mean']:.4f}"
    )
    print(
        "Mean improvement: "
        f"{summary['mean_tanimoto_improvement']:.4f}"
    )
    print(
        "Distance/Tanimoto Spearman correlation: "
        f"{summary['latent_distance_tanimoto_spearman']:.4f}"
    )


if __name__ == "__main__":
    main()