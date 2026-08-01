"""Create molecular-property-colored PCA and UMAP figures."""

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from backend.config import load_experiment_config
from backend.plot_latent_pca import (
    display_project_path,
    resolve_project_path,
)


REQUIRED_CONFIG_SECTIONS = {
    "data",
    "properties",
    "visualization",
    "artifacts",
}
ALIGNMENT_COLUMNS = ("latent_row", "id", "smiles", "split")


def parse_arguments() -> argparse.Namespace:
    """Read the selected property-visualization configuration."""
    parser = argparse.ArgumentParser(
        description=(
            "Create property-colored PCA and UMAP visualizations "
            "for QM9 latent vectors."
        )
    )
    parser.add_argument(
        "--config",
        default="configs/qm9_property_visualizations.yaml",
        help="Path to the property-visualization YAML configuration.",
    )
    return parser.parse_args()


def load_projection_metadata(
    metadata_path: Path,
    coordinate_columns: tuple[str, str],
    property_columns: tuple[str, ...],
) -> pd.DataFrame:
    """Load and validate aligned projection metadata."""
    if not metadata_path.is_file():
        raise FileNotFoundError(
            f"Projection metadata was not found: {metadata_path}"
        )

    metadata = pd.read_csv(metadata_path)
    required_columns = (
        set(ALIGNMENT_COLUMNS)
        | set(coordinate_columns)
        | set(property_columns)
    )
    missing_columns = required_columns.difference(metadata.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"Projection metadata is missing required columns: {missing}"
        )

    if metadata.empty:
        raise ValueError("Projection metadata cannot be empty.")

    if metadata["latent_row"].duplicated().any():
        raise ValueError("Projection metadata contains duplicate latent rows.")

    if metadata["id"].duplicated().any():
        raise ValueError("Projection metadata contains duplicate molecule IDs.")

    expected_rows = np.arange(len(metadata))

    if not np.array_equal(
        metadata["latent_row"].to_numpy(),
        expected_rows,
    ):
        raise ValueError(
            "latent_row must contain sequential values aligned with "
            "projection rows."
        )

    numeric_columns = coordinate_columns + property_columns
    validated_metadata = metadata.copy()

    for column in numeric_columns:
        validated_metadata[column] = pd.to_numeric(
            validated_metadata[column],
            errors="raise",
        )

        if not np.isfinite(
            validated_metadata[column].to_numpy(dtype=np.float64)
        ).all():
            raise ValueError(
                f"Projection metadata column '{column}' contains "
                "non-finite values."
            )

    return validated_metadata


def validate_projection_alignment(
    pca_metadata: pd.DataFrame,
    umap_metadata: pd.DataFrame,
    property_columns: tuple[str, ...],
) -> None:
    """Verify that PCA and UMAP rows describe the same molecules."""
    if len(pca_metadata) != len(umap_metadata):
        raise ValueError(
            "PCA and UMAP metadata must contain the same number of rows."
        )

    for column in ALIGNMENT_COLUMNS:
        if not np.array_equal(
            pca_metadata[column].to_numpy(),
            umap_metadata[column].to_numpy(),
        ):
            raise ValueError(
                f"PCA and UMAP metadata are misaligned in column '{column}'."
            )

    for column in property_columns:
        if not np.allclose(
            pca_metadata[column].to_numpy(dtype=np.float64),
            umap_metadata[column].to_numpy(dtype=np.float64),
            rtol=0.0,
            atol=1e-8,
        ):
            raise ValueError(
                f"PCA and UMAP property values differ for '{column}'."
            )


def calculate_property_statistics(
    metadata: pd.DataFrame,
    property_columns: tuple[str, ...],
    lower_quantile: float,
    upper_quantile: float,
) -> dict[str, dict[str, float]]:
    """Calculate shared property ranges for PCA and UMAP figures."""
    if not 0.0 <= lower_quantile < upper_quantile <= 1.0:
        raise ValueError(
            "Visualization quantiles must satisfy "
            "0 <= lower < upper <= 1."
        )

    statistics: dict[str, dict[str, float]] = {}

    for column in property_columns:
        values = metadata[column].to_numpy(dtype=np.float64)
        color_min = float(np.quantile(values, lower_quantile))
        color_max = float(np.quantile(values, upper_quantile))

        if color_min == color_max:
            color_min -= 0.5
            color_max += 0.5

        statistics[column] = {
            "minimum": float(values.min()),
            "maximum": float(values.max()),
            "mean": float(values.mean()),
            "median": float(np.median(values)),
            "color_minimum": color_min,
            "color_maximum": color_max,
        }

    return statistics


def save_property_figure(
    metadata: pd.DataFrame,
    coordinate_columns: tuple[str, str],
    property_config: dict[str, dict[str, str]],
    property_statistics: dict[str, dict[str, float]],
    figure_path: Path,
    title: str,
    point_size: float,
    point_alpha: float,
    figure_dpi: int,
) -> None:
    """Save a multi-panel latent projection colored by properties."""
    figure_path.parent.mkdir(parents=True, exist_ok=True)

    property_items = list(property_config.items())
    figure, axes = plt.subplots(
        2,
        3,
        figsize=(18, 11),
        dpi=figure_dpi,
    )
    flat_axes = axes.flatten()

    x_values = metadata[coordinate_columns[0]].to_numpy()
    y_values = metadata[coordinate_columns[1]].to_numpy()

    for axis, (column, settings) in zip(
        flat_axes,
        property_items,
        strict=False,
    ):
        values = metadata[column].to_numpy(dtype=np.float64)
        statistics = property_statistics[column]
        clipped_values = np.clip(
            values,
            statistics["color_minimum"],
            statistics["color_maximum"],
        )

        scatter = axis.scatter(
            x_values,
            y_values,
            c=clipped_values,
            cmap=settings["colormap"],
            vmin=statistics["color_minimum"],
            vmax=statistics["color_maximum"],
            s=point_size,
            alpha=point_alpha,
            edgecolors="none",
            rasterized=True,
        )

        axis.set_title(settings["label"], fontweight="bold")
        axis.set_xlabel(coordinate_columns[0].replace("_", " ").upper())
        axis.set_ylabel(coordinate_columns[1].replace("_", " ").upper())
        axis.grid(alpha=0.15)

        colorbar = figure.colorbar(
            scatter,
            ax=axis,
            fraction=0.046,
            pad=0.04,
        )
        colorbar.set_label(settings["label"])

    for unused_axis in flat_axes[len(property_items):]:
        unused_axis.set_visible(False)

    figure.suptitle(
        title,
        fontsize=18,
        fontweight="bold",
        y=0.995,
    )
    figure.tight_layout()
    figure.savefig(figure_path, bbox_inches="tight")
    plt.close(figure)


def create_property_visualization_artifacts(
    pca_metadata_path: Path,
    umap_metadata_path: Path,
    manifest_path: Path,
    pca_figure_path: Path,
    umap_figure_path: Path,
    property_config: dict[str, dict[str, str]],
    visualization_config: dict[str, Any],
    project_root: Path,
) -> dict[str, Any]:
    """Create property-colored PCA and UMAP figures and a manifest."""
    if not property_config:
        raise ValueError("At least one molecular property is required.")

    property_columns = tuple(property_config)

    for column, settings in property_config.items():
        if "label" not in settings or "colormap" not in settings:
            raise ValueError(
                f"Property '{column}' requires label and colormap values."
            )

    pca_metadata = load_projection_metadata(
        metadata_path=pca_metadata_path,
        coordinate_columns=("pca_1", "pca_2"),
        property_columns=property_columns,
    )
    umap_metadata = load_projection_metadata(
        metadata_path=umap_metadata_path,
        coordinate_columns=("umap_1", "umap_2"),
        property_columns=property_columns,
    )

    validate_projection_alignment(
        pca_metadata=pca_metadata,
        umap_metadata=umap_metadata,
        property_columns=property_columns,
    )

    lower_quantile = float(
        visualization_config["lower_quantile"]
    )
    upper_quantile = float(
        visualization_config["upper_quantile"]
    )
    point_size = float(visualization_config["point_size"])
    point_alpha = float(visualization_config["point_alpha"])
    figure_dpi = int(visualization_config["figure_dpi"])

    if point_size <= 0:
        raise ValueError("Visualization point_size must be positive.")

    if not 0.0 < point_alpha <= 1.0:
        raise ValueError(
            "Visualization point_alpha must be in the interval (0, 1]."
        )

    if figure_dpi <= 0:
        raise ValueError("Visualization figure_dpi must be positive.")

    property_statistics = calculate_property_statistics(
        metadata=pca_metadata,
        property_columns=property_columns,
        lower_quantile=lower_quantile,
        upper_quantile=upper_quantile,
    )

    save_property_figure(
        metadata=pca_metadata,
        coordinate_columns=("pca_1", "pca_2"),
        property_config=property_config,
        property_statistics=property_statistics,
        figure_path=pca_figure_path,
        title="QM9 Fingerprint VAE latent space: PCA by property",
        point_size=point_size,
        point_alpha=point_alpha,
        figure_dpi=figure_dpi,
    )
    save_property_figure(
        metadata=umap_metadata,
        coordinate_columns=("umap_1", "umap_2"),
        property_config=property_config,
        property_statistics=property_statistics,
        figure_path=umap_figure_path,
        title="QM9 Fingerprint VAE latent space: UMAP by property",
        point_size=point_size,
        point_alpha=point_alpha,
        figure_dpi=figure_dpi,
    )

    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    manifest = {
        "artifact_schema_version": 1,
        "analysis": "molecular_property_latent_visualization",
        "dataset_size": len(pca_metadata),
        "properties": {
            column: {
                "label": settings["label"],
                "colormap": settings["colormap"],
                **property_statistics[column],
            }
            for column, settings in property_config.items()
        },
        "visualization": {
            "lower_quantile": lower_quantile,
            "upper_quantile": upper_quantile,
            "point_size": point_size,
            "point_alpha": point_alpha,
            "figure_dpi": figure_dpi,
        },
        "inputs": {
            "pca_metadata_path": display_project_path(
                project_root,
                pca_metadata_path,
            ),
            "umap_metadata_path": display_project_path(
                project_root,
                umap_metadata_path,
            ),
        },
        "outputs": {
            "pca_figure_path": display_project_path(
                project_root,
                pca_figure_path,
            ),
            "umap_figure_path": display_project_path(
                project_root,
                umap_figure_path,
            ),
        },
        "split_sizes": {
            split_name: int(
                (pca_metadata["split"] == split_name).sum()
            )
            for split_name in ("train", "validation", "test")
        },
    }

    manifest_path.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    return manifest


def main() -> None:
    """Create configured molecular-property latent figures."""
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

    manifest = create_property_visualization_artifacts(
        pca_metadata_path=resolve_project_path(
            project_root,
            data_config["pca_metadata_path"],
        ),
        umap_metadata_path=resolve_project_path(
            project_root,
            data_config["umap_metadata_path"],
        ),
        manifest_path=resolve_project_path(
            project_root,
            artifact_config["manifest_path"],
        ),
        pca_figure_path=resolve_project_path(
            project_root,
            artifact_config["pca_figure_path"],
        ),
        umap_figure_path=resolve_project_path(
            project_root,
            artifact_config["umap_figure_path"],
        ),
        property_config=config["properties"],
        visualization_config=config["visualization"],
        project_root=project_root,
    )

    print(f"Analysis: {manifest['analysis']}")
    print(f"Molecules: {manifest['dataset_size']}")
    print(
        "Properties: "
        + ", ".join(manifest["properties"])
    )
    print(
        f"PCA figure: {manifest['outputs']['pca_figure_path']}"
    )
    print(
        f"UMAP figure: {manifest['outputs']['umap_figure_path']}"
    )


if __name__ == "__main__":
    main()