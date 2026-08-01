"""Create a reproducible UMAP projection of QM9 latent vectors."""

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from umap import UMAP

from backend.config import load_experiment_config
from backend.plot_latent_pca import (
    display_project_path,
    load_export_manifest,
    load_latent_metadata,
    load_latent_vectors,
    resolve_project_path,
)


REQUIRED_UMAP_SECTIONS = {"data", "projection", "artifacts"}
SPLIT_COLORS = {
    "train": "#2563eb",
    "validation": "#f59e0b",
    "test": "#dc2626",
}


def parse_arguments() -> argparse.Namespace:
    """Read the selected UMAP configuration path."""
    parser = argparse.ArgumentParser(
        description="Create a UMAP projection of QM9 latent vectors."
    )
    parser.add_argument(
        "--config",
        default="configs/qm9_latent_umap.yaml",
        help="Path to the UMAP YAML configuration.",
    )
    return parser.parse_args()


def fit_umap_projection(
    latent_vectors: np.ndarray,
    split_labels: np.ndarray,
    components: int,
    fit_split: str,
    n_neighbors: int,
    min_dist: float,
    metric: str,
    random_state: int,
    transform_seed: int,
) -> np.ndarray:
    """Fit UMAP on one split and transform every molecule."""
    if components < 2:
        raise ValueError("UMAP must produce at least two components.")

    if n_neighbors < 2:
        raise ValueError("UMAP n_neighbors must be at least 2.")

    if min_dist < 0:
        raise ValueError("UMAP min_dist cannot be negative.")

    if not np.isfinite(latent_vectors).all():
        raise ValueError("Latent vectors must contain only finite values.")

    fit_mask = split_labels == fit_split

    if not np.any(fit_mask):
        raise ValueError(
            f"No molecules were found in the '{fit_split}' split."
        )

    fitting_vectors = latent_vectors[fit_mask]

    if len(fitting_vectors) <= n_neighbors:
        raise ValueError(
            "The UMAP fitting split must contain more molecules than "
            "n_neighbors."
        )

    projector = UMAP(
        n_components=components,
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        metric=metric,
        random_state=random_state,
        transform_seed=transform_seed,
        n_jobs=1,
    )
    projector.fit(fitting_vectors)

    coordinates = projector.transform(latent_vectors)

    if not np.isfinite(coordinates).all():
        raise ValueError("UMAP produced non-finite coordinates.")

    return coordinates.astype(np.float32)


def save_umap_figure(
    coordinates: np.ndarray,
    metadata: pd.DataFrame,
    figure_path: Path,
) -> None:
    """Save a UMAP scatter plot colored by dataset split."""
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
        "QM9 Fingerprint VAE latent space: UMAP projection",
        fontweight="bold",
        pad=14,
    )
    axis.set_xlabel("UMAP component 1")
    axis.set_ylabel("UMAP component 2")
    axis.grid(alpha=0.2)
    axis.legend(frameon=False, loc="best")

    figure.tight_layout()
    figure.savefig(figure_path, bbox_inches="tight")
    plt.close(figure)


def create_umap_artifacts(
    latent_vectors_path: Path,
    latent_metadata_path: Path,
    latent_export_manifest_path: Path,
    coordinates_path: Path,
    metadata_path: Path,
    manifest_path: Path,
    figure_path: Path,
    components: int,
    fit_split: str,
    n_neighbors: int,
    min_dist: float,
    metric: str,
    random_state: int,
    transform_seed: int,
    project_root: Path,
) -> dict[str, Any]:
    """Create aligned UMAP coordinates, metadata, manifest, and figure."""
    latent_vectors = load_latent_vectors(latent_vectors_path)
    metadata = load_latent_metadata(
        latent_metadata_path,
        dataset_size=len(latent_vectors),
    )
    latent_export_manifest = load_export_manifest(
        latent_export_manifest_path
    )

    coordinates = fit_umap_projection(
        latent_vectors=latent_vectors,
        split_labels=metadata["split"].to_numpy(),
        components=components,
        fit_split=fit_split,
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        metric=metric,
        random_state=random_state,
        transform_seed=transform_seed,
    )

    umap_metadata = metadata.copy()
    umap_metadata["umap_1"] = coordinates[:, 0]
    umap_metadata["umap_2"] = coordinates[:, 1]

    coordinates_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    np.save(coordinates_path, coordinates)
    umap_metadata.to_csv(metadata_path, index=False)

    save_umap_figure(
        coordinates=coordinates,
        metadata=metadata,
        figure_path=figure_path,
    )

    manifest = {
        "artifact_schema_version": 1,
        "projection_method": "UMAP",
        "components": components,
        "fit_split": fit_split,
        "dataset_size": len(latent_vectors),
        "input_latent_dimensions": int(latent_vectors.shape[1]),
        "parameters": {
            "n_neighbors": n_neighbors,
            "min_dist": min_dist,
            "metric": metric,
            "random_state": random_state,
            "transform_seed": transform_seed,
        },
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
    """Create the configured QM9 latent UMAP artifacts."""
    arguments = parse_arguments()
    project_root = Path(__file__).resolve().parent.parent
    config_path = Path(arguments.config)

    if not config_path.is_absolute():
        config_path = project_root / config_path

    config = load_experiment_config(
        config_path,
        required_sections=REQUIRED_UMAP_SECTIONS,
    )

    data_config = config["data"]
    projection_config = config["projection"]
    artifact_config = config["artifacts"]

    manifest = create_umap_artifacts(
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
        n_neighbors=int(projection_config["n_neighbors"]),
        min_dist=float(projection_config["min_dist"]),
        metric=str(projection_config["metric"]),
        random_state=int(projection_config["random_state"]),
        transform_seed=int(projection_config["transform_seed"]),
        project_root=project_root,
    )

    print(f"Projection method: {manifest['projection_method']}")
    print(f"UMAP fitting split: {manifest['fit_split']}")
    print(f"Projected molecules: {manifest['dataset_size']}")
    print(
        f"Input latent dimensions: "
        f"{manifest['input_latent_dimensions']}"
    )
    print(f"Parameters: {manifest['parameters']}")
    print(f"Figure: {manifest['outputs']['figure_path']}")


if __name__ == "__main__":
    main()