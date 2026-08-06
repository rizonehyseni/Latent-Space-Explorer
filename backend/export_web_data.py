"""Export aligned QM9 artifacts for the web application."""

import json
import math
from numbers import Integral, Real
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

def normalize_numeric_value(
    value: Any,
    precision: int,
) -> int | float | None:
    """Convert NumPy and Pandas values into valid JSON numbers."""
    if pd.isna(value):
        return None

    if isinstance(value, Integral):
        return int(value)

    if isinstance(value, Real):
        numeric_value = float(value)

        if not math.isfinite(numeric_value):
            raise ValueError(
                "Web-export numeric values must be finite."
            )

        return round(numeric_value, precision)

    raise ValueError(
        f"Unsupported numeric value for web export: {value!r}"
    )


def create_molecule_payload(
    molecule_table: pd.DataFrame,
    experiment_name: str,
    dataset_name: str,
    schema_version: int,
    coordinate_precision: int,
    property_precision: int,
    property_columns: list[str],
) -> dict[str, Any]:
    """Convert aligned metadata into the browser data contract."""
    if schema_version <= 0:
        raise ValueError("Schema version must be positive.")

    molecules: list[dict[str, Any]] = []

    for row in molecule_table.itertuples(index=False):
        row_values = row._asdict()

        properties = {
            property_name: normalize_numeric_value(
                row_values[property_name],
                property_precision,
            )
            for property_name in property_columns
        }

        molecules.append(
            {
                "row": int(row_values["latent_row"]),
                "sourceIndex": int(
                    row_values["source_index"]
                ),
                "id": str(row_values["id"]),
                "smiles": str(row_values["smiles"]),
                "split": str(row_values["split"]),
                "coordinates": {
                    "pca": [
                        normalize_numeric_value(
                            row_values["pca_1"],
                            coordinate_precision,
                        ),
                        normalize_numeric_value(
                            row_values["pca_2"],
                            coordinate_precision,
                        ),
                    ],
                    "umap": [
                        normalize_numeric_value(
                            row_values["umap_1"],
                            coordinate_precision,
                        ),
                        normalize_numeric_value(
                            row_values["umap_2"],
                            coordinate_precision,
                        ),
                    ],
                },
                "properties": properties,
            }
        )

    split_counts = {
        split_name: int(
            (molecule_table["split"] == split_name).sum()
        )
        for split_name in [
            "train",
            "validation",
            "test",
        ]
    }

    return {
        "schemaVersion": schema_version,
        "experimentName": experiment_name,
        "dataset": {
            "name": dataset_name,
            "moleculeCount": len(molecules),
            "splitCounts": split_counts,
            "coordinateSystems": [
                "pca",
                "umap",
            ],
            "properties": property_columns,
        },
        "molecules": molecules,
    }


def write_json_artifact(
    payload: dict[str, Any],
    artifact_path: Path,
) -> None:
    """Write deterministic compact JSON for browser loading."""
    artifact_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    artifact_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )

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


    property_columns = [
        str(property_name)
        for property_name in export_config["properties"]
    ]

    molecule_table = create_aligned_molecule_table(
        pca_metadata_path=resolve_project_path(
            project_root,
            data_config["pca_metadata_path"],
        ),
        umap_metadata_path=resolve_project_path(
            project_root,
            data_config["umap_metadata_path"],
        ),
        property_columns=property_columns,
    )

    split_counts = molecule_table["split"].value_counts()

    
    molecule_payload = create_molecule_payload(
        molecule_table=molecule_table,
        experiment_name=str(config["experiment_name"]),
        dataset_name=str(export_config["dataset_name"]),
        schema_version=int(export_config["schema_version"]),
        coordinate_precision=int(
            export_config["coordinate_precision"]
        ),
        property_precision=int(
            export_config["property_precision"]
        ),
        property_columns=property_columns,
    )


    molecules_path = resolve_project_path(
        project_root,
        config["artifacts"]["molecules_path"],
    )
    write_json_artifact(
        payload=molecule_payload,
        artifact_path=molecules_path,
    )
    

    print(f"Aligned molecules: {len(molecule_table)}")
    print(f"Training molecules: {split_counts.get('train', 0)}")
    print(
        "Validation molecules: "
        f"{split_counts.get('validation', 0)}"
    )
    print(f"Test molecules: {split_counts.get('test', 0)}")
    print("Projection metadata alignment: valid")
    print(f"Molecule JSON saved to: {molecules_path}")


if __name__ == "__main__":
    main()