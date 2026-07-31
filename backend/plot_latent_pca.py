"""Create a reproducible PCA projection of QM9 latent vectors."""

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

from backend.config import load_experiment_config


REQUIRED_PCA_SECTIONS = {"data", "projection", "artifacts"}
REQUIRED_METADATA_COLUMNS = {"latent_row", "id", "smiles", "split"}
SPLIT_COLORS = {
    "train": "#2563eb",
    "validation": "#f59e0b",
    "test": "#dc2626",
}


def parse_arguments() -> argparse.Namespace:
    """Read the selected PCA configuration path."""
    parser = argparse.ArgumentParser(
        description="Create a PCA projection of QM9 latent vectors."
    )
    parser.add_argument(
        "--config",
        default="configs/qm9_latent_pca.yaml",
        help="Path to the PCA YAML configuration.",
    )
    return parser.parse_args()


def resolve_project_path(project_root: Path, path_value: str) -> Path:
    """Resolve a configuration path relative to the project root."""
    path = Path(path_value)
    return path if path.is_absolute() else project_root / path


def display_project_path(project_root: Path, path: Path) -> str:
    """Display project-relative paths when possible."""
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def load_latent_vectors(latent_vectors_path: Path) -> np.ndarray:
    """Load the two-dimensional latent-vector matrix."""
    if not latent_vectors_path.is_file():
        raise FileNotFoundError(
            f"Latent-vector artifact was not found: {latent_vectors_path}"
        )

    latent_vectors = np.load(latent_vectors_path)

    if latent_vectors.ndim != 2:
        raise ValueError(
            "Latent vectors must be a 2D matrix with shape "
            "(molecules, latent_dimensions)."
        )

    if len(latent_vectors) == 0:
        raise ValueError("Latent-vector artifact is empty.")

    return latent_vectors.astype(np.float32)


def load_latent_metadata(
    latent_metadata_path: Path,
    dataset_size: int,
) -> pd.DataFrame:
    """Load metadata and verify row alignment with latent vectors."""
    if not latent_metadata_path.is_file():
        raise FileNotFoundError(
            f"Latent metadata artifact was not found: {latent_metadata_path}"
        )

    metadata = pd.read_csv(latent_metadata_path)
    missing_columns = REQUIRED_METADATA_COLUMNS.difference(metadata.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"Latent metadata is missing required columns: {missing}"
        )

    if len(metadata) != dataset_size:
        raise ValueError(
            "Latent metadata row count must match the latent-vector count."
        )

    expected_rows = np.arange(dataset_size)

    if not np.array_equal(
        metadata["latent_row"].to_numpy(),
        expected_rows,
    ):
        raise ValueError(
            "latent_row must contain sequential values aligned with "
            "latent-vector rows."
        )

    return metadata


def load_export_manifest(manifest_path: Path) -> dict[str, Any]:
    """Load the latent-export provenance manifest."""
    if not manifest_path.is_file():
        raise FileNotFoundError(
            f"Latent-export manifest was not found: {manifest_path}"
        )

    return json.loads(manifest_path.read_text(encoding="utf-8"))


def fit_pca_projection(
    latent_vectors: np.ndarray,
    split_labels: np.ndarray,
    components: int,
    fit_split: str,
) -> tuple[np.ndarray, np.ndarray]:
    """Fit PCA on one split and transform every molecule."""
    fit_mask = split_labels == fit_split

    if not np.any(fit_mask):
        raise ValueError(f"No molecules were found in the '{fit_split}' split.")

    fitting_vectors = latent_vectors[fit_mask]

    if len(fitting_vectors) < components:
        raise ValueError(
            "The PCA fitting split must contain at least as many molecules "
            "as requested components."
        )

    if latent_vectors.shape[1] < components:
        raise ValueError(
            "Latent dimensionality must be at least the requested "
            "number of PCA components."
        )

    pca = PCA(n_components=components, svd_solver="full")
    pca.fit(fitting_vectors)

    coordinates = pca.transform(latent_vectors).astype(np.float32)
    explained_variance_ratio = pca.explained_variance_ratio_.astype(np.float64)

    return coordinates, explained_variance_ratio


def save_pca_figure(
    coordinates: np.ndarray,
    metadata: pd.DataFrame,
    explained_variance_ratio: np.ndarray,
    figure_path: Path,
) -> None:
    """Save a PCA scatter plot colored by dataset split."""
    figure_path.parent.mkdir(parents=True, exist_ok=True)

    figure, axis = plt.subplots(figsize=(10, 8), dpi=160)

    for split_name in ("train", "validation", "test"):
        split_mask = metadata["split"] == split_name

        axis.scatter(
            coordinates[split_mask, 0],
            coordinates[split_mask, 1],
            s=10,
            alpha=0.65,
            color=SPLIT_COLORS[split_name],
            edgecolors="none",
            label=f"{split_name.title()} ({int(split_mask.sum()):,})",
        )

    axis.set_title(
        "QM9 Fingerprint VAE latent space: PCA projection",
        fontweight="bold",
        pad=14,
    )
    axis.set_xlabel(
        f"Principal component 1 "
        f"({explained_variance_ratio[0] * 100:.1f}% variance)"
    )
    axis.set_ylabel(
        f"Principal component 2 "
        f"({explained_variance_ratio[1] * 100:.1f}% variance)"
    )
    axis.grid(alpha=0.2)
    axis.legend(frameon=False, loc="best")

    figure.tight_layout()
    figure.savefig(figure_path, bbox_inches="tight")
    plt.close(figure)


def create_pca_artifacts(
    latent_vectors_path: Path,
    latent_metadata_path: Path,
    latent_export_manifest_path: Path,
    coordinates_path: Path,
    metadata_path: Path,
    manifest_path: Path,
    figure_path: Path,
    components: int,
    fit_split: str,
    project_root: Path,
) -> dict[str, Any]:
    """Create PCA coordinates, aligned metadata, manifest, and figure."""
    latent_vectors = load_latent_vectors(latent_vectors_path)
    metadata = load_latent_metadata(
        latent_metadata_path,
        dataset_size=len(latent_vectors),
    )
    latent_export_manifest = load_export_manifest(latent_export_manifest_path)

    coordinates, explained_variance_ratio = fit_pca_projection(
        latent_vectors=latent_vectors,
        split_labels=metadata["split"].to_numpy(),
        components=components,
        fit_split=fit_split,
    )

    pca_metadata = metadata.copy()
    pca_metadata["pca_1"] = coordinates[:, 0]
    pca_metadata["pca_2"] = coordinates[:, 1]

    coordinates_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    np.save(coordinates_path, coordinates)
    pca_metadata.to_csv(metadata_path, index=False)

    save_pca_figure(
        coordinates=coordinates,
        metadata=metadata,
        explained_variance_ratio=explained_variance_ratio,
        figure_path=figure_path,
    )

    manifest = {
        "artifact_schema_version": 1,
        "projection_method": "PCA",
        "components": components,
        "fit_split": fit_split,
        "dataset_size": len(latent_vectors),
        "input_latent_dimensions": int(latent_vectors.shape[1]),
        "explained_variance_ratio": explained_variance_ratio.tolist(),
        "total_explained_variance": float(explained_variance_ratio.sum()),
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
            "latent_metadata_path": display_project_path(
                project_root,
                latent_metadata_path,
            ),
            "latent_export_manifest_path": display_project_path(
                project_root,
                latent_export_manifest_path,
            ),
        },
        "outputs": {
            "coordinates_path": display_project_path(
                project_root,
                coordinates_path,
            ),
            "metadata_path": display_project_path(
                project_root,
                metadata_path,
            ),
            "figure_path": display_project_path(
                project_root,
                figure_path,
            ),
        },
        "split_sizes": {
            split_name: int((metadata["split"] == split_name).sum())
            for split_name in ("train", "validation", "test")
        },
    }

    manifest_path.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    return manifest


def main() -> None:
    """Create the configured QM9 latent PCA artifacts."""
    arguments = parse_arguments()
    project_root = Path(__file__).resolve().parent.parent

    config_path = Path(arguments.config)

    if not config_path.is_absolute():
        config_path = project_root / config_path

    config = load_experiment_config(
        config_path,
        required_sections=REQUIRED_PCA_SECTIONS,
    )

    data_config = config["data"]
    projection_config = config["projection"]
    artifact_config = config["artifacts"]

    manifest = create_pca_artifacts(
        latent_vectors_path=resolve_project_path(
            project_root,
            data_config["latent_vectors_path"],
        ),
        latent_metadata_path=resolve_project_path(
            project_root,
            data_config["latent_metadata_path"],
        ),
        latent_export_manifest_path=resolve_project_path(
            project_root,
            data_config["latent_export_manifest_path"],
        ),
        coordinates_path=resolve_project_path(
            project_root,
            artifact_config["coordinates_path"],
        ),
        metadata_path=resolve_project_path(
            project_root,
            artifact_config["metadata_path"],
        ),
        manifest_path=resolve_project_path(
            project_root,
            artifact_config["manifest_path"],
        ),
        figure_path=resolve_project_path(
            project_root,
            artifact_config["figure_path"],
        ),
        components=int(projection_config["components"]),
        fit_split=str(projection_config["fit_split"]),
        project_root=project_root,
    )

    explained_variance = manifest["explained_variance_ratio"]

    print(f"Projection method: {manifest['projection_method']}")
    print(f"PCA fitting split: {manifest['fit_split']}")
    print(f"Projected molecules: {manifest['dataset_size']}")
    print(f"Input latent dimensions: {manifest['input_latent_dimensions']}")
    print(
        "Explained variance ratio: "
        f"PC1={explained_variance[0]:.4f}, "
        f"PC2={explained_variance[1]:.4f}"
    )
    print(
        "Total explained variance: "
        f"{manifest['total_explained_variance']:.4f}"
    )
    print(f"Figure: {manifest['outputs']['figure_path']}")


if __name__ == "__main__":
    main()