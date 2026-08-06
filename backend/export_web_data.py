"""Export aligned QM9 artifacts for the web application."""

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

from backend.config import load_experiment_config


REQUIRED_CONFIG_SECTIONS = {
    "data",
    "export",
    "artifacts",
}

IDENTITY_COLUMNS = [
    "latent_row",
    "source_index",
    "id",
    "smiles",
    "split",
]

PCA_COORDINATE_COLUMNS = [
    "pca_1",
    "pca_2",
]

UMAP_COORDINATE_COLUMNS = [
    "umap_1",
    "umap_2",
]


def parse_arguments() -> argparse.Namespace:
    """Read the selected web-export configuration path."""
    parser = argparse.ArgumentParser(
        description="Export aligned QM9 data for the web application."
    )
    parser.add_argument(
        "--config",
        default="configs/qm9_web_export.yaml",
        help="Path to the web-export YAML configuration.",
    )
    return parser.parse_args()


def resolve_project_path(
    project_root: Path,
    configured_path: str,
) -> Path:
    """Resolve a configured project-relative path."""
    path = Path(configured_path)

    if path.is_absolute():
        return path

    return project_root / path


def require_columns(
    frame: pd.DataFrame,
    required_columns: list[str],
    artifact_name: str,
) -> None:
    """Raise an informative error for missing columns."""
    missing_columns = [
        column
        for column in required_columns
        if column not in frame.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{artifact_name} is missing required columns: "
            + ", ".join(missing_columns)
        )


def load_projection_metadata(
    metadata_path: Path,
    required_columns: list[str],
    artifact_name: str,
) -> pd.DataFrame:
    """Load and validate one projection metadata artifact."""
    if not metadata_path.is_file():
        raise FileNotFoundError(
            f"{artifact_name} was not found: {metadata_path}"
        )

    metadata = pd.read_csv(metadata_path)

    if metadata.empty:
        raise ValueError(f"{artifact_name} cannot be empty.")

    require_columns(
        frame=metadata,
        required_columns=required_columns,
        artifact_name=artifact_name,
    )

    if metadata["latent_row"].duplicated().any():
        raise ValueError(
            f"{artifact_name} contains duplicate latent rows."
        )

    if metadata["id"].duplicated().any():
        raise ValueError(
            f"{artifact_name} contains duplicate molecule IDs."
        )

    return metadata


def create_aligned_molecule_table(
    pca_metadata_path: Path,
    umap_metadata_path: Path,
    property_columns: list[str],
) -> pd.DataFrame:
    """Align PCA, UMAP, identity, split, and property data."""
    shared_columns = IDENTITY_COLUMNS + property_columns

    pca_metadata = load_projection_metadata(
        metadata_path=pca_metadata_path,
        required_columns=(
            shared_columns + PCA_COORDINATE_COLUMNS
        ),
        artifact_name="PCA metadata",
    )
    umap_metadata = load_projection_metadata(
        metadata_path=umap_metadata_path,
        required_columns=(
            shared_columns + UMAP_COORDINATE_COLUMNS
        ),
        artifact_name="UMAP metadata",
    )

    if len(pca_metadata) != len(umap_metadata):
        raise ValueError(
            "PCA and UMAP metadata row counts do not match."
        )

    for column in shared_columns:
        if not pca_metadata[column].equals(
            umap_metadata[column]
        ):
            raise ValueError(
                "PCA and UMAP metadata are not aligned for "
                f"column: {column}"
            )

    molecule_table = pca_metadata[
        shared_columns + PCA_COORDINATE_COLUMNS
    ].copy()

    for column in UMAP_COORDINATE_COLUMNS:
        molecule_table[column] = umap_metadata[column]

    return molecule_table


def load_web_export_config(
    config_path: Path,
) -> dict[str, Any]:
    """Load and validate the web-export configuration."""
    return load_experiment_config(
        config_path=config_path,
        required_sections=REQUIRED_CONFIG_SECTIONS,
    )


def main() -> None:
    """Validate the browser-ready molecule data sources."""
    arguments = parse_arguments()
    project_root = Path(__file__).resolve().parent.parent

    config_path = Path(arguments.config)
    if not config_path.is_absolute():
        config_path = project_root / config_path

    config = load_web_export_config(config_path)
    data_config = config["data"]
    export_config = config["export"]

    molecule_table = create_aligned_molecule_table(
        pca_metadata_path=resolve_project_path(
            project_root,
            data_config["pca_metadata_path"],
        ),
        umap_metadata_path=resolve_project_path(
            project_root,
            data_config["umap_metadata_path"],
        ),
        property_columns=[
            str(property_name)
            for property_name in export_config["properties"]
        ],
    )

    split_counts = molecule_table["split"].value_counts()

    print(f"Aligned molecules: {len(molecule_table)}")
    print(f"Training molecules: {split_counts.get('train', 0)}")
    print(
        "Validation molecules: "
        f"{split_counts.get('validation', 0)}"
    )
    print(f"Test molecules: {split_counts.get('test', 0)}")
    print("Projection metadata alignment: valid")


if __name__ == "__main__":
    main()