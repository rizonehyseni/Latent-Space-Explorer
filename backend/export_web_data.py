"""Export aligned QM9 artifacts for the web application."""

import json
import math
import hashlib
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

def load_neighbor_results(
    neighbor_results_path: Path,
) -> pd.DataFrame:
    """Load and validate latent-neighbor results."""
    if not neighbor_results_path.is_file():
        raise FileNotFoundError(
            "Neighbor results were not found: "
            f"{neighbor_results_path}"
        )

    neighbor_results = pd.read_csv(neighbor_results_path)

    required_columns = [
        "query_latent_row",
        "query_id",
        "query_split",
        "neighbor_rank",
        "neighbor_latent_row",
        "neighbor_id",
        "reference_split",
        "latent_distance",
        "tanimoto_similarity",
    ]

    require_columns(
        frame=neighbor_results,
        required_columns=required_columns,
        artifact_name="Neighbor results",
    )

    if neighbor_results.empty:
        raise ValueError("Neighbor results cannot be empty.")

    return neighbor_results


def create_neighbor_payload(
    neighbor_results_path: Path,
    molecule_table: pd.DataFrame,
    schema_version: int,
    neighbors_per_query: int,
    numeric_precision: int,
) -> dict[str, Any]:
    """Create aligned browser data for latent neighbors."""
    if neighbors_per_query <= 0:
        raise ValueError(
            "Neighbors per query must be positive."
        )

    neighbor_results = load_neighbor_results(
        neighbor_results_path
    )
    neighbor_results = neighbor_results[
        neighbor_results["neighbor_rank"]
        <= neighbors_per_query
    ].copy()

    molecule_lookup = molecule_table.set_index("latent_row")
    queries: dict[str, Any] = {}

    grouped_results = neighbor_results.groupby(
        "query_latent_row",
        sort=True,
    )

    for query_row_value, query_results in grouped_results:
        query_row = int(query_row_value)
        query_results = query_results.sort_values(
            "neighbor_rank"
        )

        expected_ranks = list(
            range(1, neighbors_per_query + 1)
        )
        actual_ranks = [
            int(rank)
            for rank in query_results["neighbor_rank"]
        ]

        if actual_ranks != expected_ranks:
            raise ValueError(
                "Neighbor ranks are incomplete for query row: "
                f"{query_row}"
            )

        if query_row not in molecule_lookup.index:
            raise ValueError(
                f"Unknown query latent row: {query_row}"
            )

        query_molecule = molecule_lookup.loc[query_row]
        query_id = str(query_molecule["id"])

        recorded_query_ids = set(
            query_results["query_id"].astype(str)
        )
        if recorded_query_ids != {query_id}:
            raise ValueError(
                "Neighbor query ID does not match molecule data "
                f"for row: {query_row}"
            )

        if str(query_molecule["split"]) != "test":
            raise ValueError(
                "Neighbor query must belong to the test split."
            )

        neighbors: list[dict[str, Any]] = []

        for result in query_results.itertuples(index=False):
            neighbor_row = int(result.neighbor_latent_row)

            if neighbor_row not in molecule_lookup.index:
                raise ValueError(
                    f"Unknown neighbor latent row: {neighbor_row}"
                )

            neighbor_molecule = molecule_lookup.loc[
                neighbor_row
            ]
            neighbor_id = str(neighbor_molecule["id"])

            if neighbor_id != str(result.neighbor_id):
                raise ValueError(
                    "Neighbor ID does not match molecule data "
                    f"for row: {neighbor_row}"
                )

            if str(neighbor_molecule["split"]) != "train":
                raise ValueError(
                    "Neighbor reference must belong to "
                    "the training split."
                )

            neighbors.append(
                {
                    "rank": int(result.neighbor_rank),
                    "row": neighbor_row,
                    "id": neighbor_id,
                    "latentDistance": normalize_numeric_value(
                        result.latent_distance,
                        numeric_precision,
                    ),
                    "tanimoto": normalize_numeric_value(
                        result.tanimoto_similarity,
                        numeric_precision,
                    ),
                }
            )

        queries[query_id] = {
            "queryRow": query_row,
            "neighbors": neighbors,
        }

    return {
        "schemaVersion": schema_version,
        "queryCount": len(queries),
        "neighborsPerQuery": neighbors_per_query,
        "queries": queries,
    }

def load_json_object(
    artifact_path: Path,
    artifact_name: str,
) -> dict[str, Any]:
    """Load one JSON summary artifact."""
    if not artifact_path.is_file():
        raise FileNotFoundError(
            f"{artifact_name} was not found: {artifact_path}"
        )

    payload = json.loads(
        artifact_path.read_text(encoding="utf-8")
    )

    if not isinstance(payload, dict):
        raise ValueError(
            f"{artifact_name} must contain a JSON object."
        )

    return payload


def create_statistic_payload(
    statistics: dict[str, Any],
    precision: int,
) -> dict[str, int | float | None]:
    """Convert aggregate statistics to browser-safe values."""
    return {
        "mean": normalize_numeric_value(
            statistics["mean"],
            precision,
        ),
        "standardDeviation": normalize_numeric_value(
            statistics["standard_deviation"],
            precision,
        ),
        "minimum": normalize_numeric_value(
            statistics["minimum"],
            precision,
        ),
        "maximum": normalize_numeric_value(
            statistics["maximum"],
            precision,
        ),
    }


def create_metrics_payload(
    neighbor_summary_path: Path,
    reconstruction_summary_path: Path,
    robustness_summary_path: Path,
    schema_version: int,
    numeric_precision: int,
) -> dict[str, Any]:
    """Create a compact scientific summary for the frontend."""
    neighbor = load_json_object(
        neighbor_summary_path,
        "Neighbor summary",
    )
    reconstruction = load_json_object(
        reconstruction_summary_path,
        "Reconstruction summary",
    )
    robustness = load_json_object(
        robustness_summary_path,
        "Robustness summary",
    )

    neighbor_by_rank = [
        {
            "rank": int(rank),
            "meanTanimoto": normalize_numeric_value(
                value,
                numeric_precision,
            ),
        }
        for rank, value in sorted(
            neighbor["mean_tanimoto_by_rank"].items(),
            key=lambda item: int(item[0]),
        )
    ]

    reconstruction_metrics = reconstruction["model_metrics"]
    reference_evaluation = reconstruction[
        "reference_threshold_evaluation"
    ]
    reference_metrics = reference_evaluation["model_metrics"]
    all_zero_metrics = reconstruction["all_zero_baseline"]

    threshold_sweep = [
        {
            "threshold": normalize_numeric_value(
                result["threshold"],
                numeric_precision,
            ),
            "precision": normalize_numeric_value(
                result["precision"],
                numeric_precision,
            ),
            "recall": normalize_numeric_value(
                result["recall"],
                numeric_precision,
            ),
            "f1Score": normalize_numeric_value(
                result["f1_score"],
                numeric_precision,
            ),
            "meanTanimoto": normalize_numeric_value(
                result["mean_tanimoto"],
                numeric_precision,
            ),
        }
        for result in reconstruction[
            "threshold_selection"
        ]["sweep"]
    ]

    robustness_by_dimension = []

    for latent_dimension in robustness["latent_dimensions"]:
        aggregate = robustness[
            "aggregate_by_latent_dimension"
        ][str(latent_dimension)]

        robustness_by_dimension.append(
            {
                "latentDimensions": int(latent_dimension),
                "runCount": int(aggregate["run_count"]),
                "testLoss": create_statistic_payload(
                    aggregate["test_loss"],
                    numeric_precision,
                ),
                "f1Score": create_statistic_payload(
                    aggregate["f1_score"],
                    numeric_precision,
                ),
                "meanTanimoto": create_statistic_payload(
                    aggregate["mean_tanimoto"],
                    numeric_precision,
                ),
                "selectedThreshold": (
                    create_statistic_payload(
                        aggregate["selected_threshold"],
                        numeric_precision,
                    )
                ),
            }
        )

    return {
        "schemaVersion": schema_version,
        "neighborAnalysis": {
            "queryCount": int(neighbor["query_count"]),
            "referenceCount": int(
                neighbor["reference_count"]
            ),
            "neighborsPerQuery": int(
                neighbor["neighbors_per_query"]
            ),
            "distanceMetric": str(
                neighbor["latent_distance_metric"]
            ),
            "meanNeighborTanimoto": normalize_numeric_value(
                neighbor["nearest_neighbor_tanimoto"]["mean"],
                numeric_precision,
            ),
            "medianNeighborTanimoto": normalize_numeric_value(
                neighbor["nearest_neighbor_tanimoto"]["median"],
                numeric_precision,
            ),
            "meanRandomTanimoto": normalize_numeric_value(
                neighbor["random_baseline_tanimoto"]["mean"],
                numeric_precision,
            ),
            "meanImprovement": normalize_numeric_value(
                neighbor["mean_tanimoto_improvement"],
                numeric_precision,
            ),
            "neighborBeatsRandomFraction": (
                normalize_numeric_value(
                    neighbor[
                        "nearest_beats_paired_random_fraction"
                    ],
                    numeric_precision,
                )
            ),
            "pearsonCorrelation": normalize_numeric_value(
                neighbor[
                    "latent_distance_tanimoto_pearson"
                ],
                numeric_precision,
            ),
            "spearmanCorrelation": normalize_numeric_value(
                neighbor[
                    "latent_distance_tanimoto_spearman"
                ],
                numeric_precision,
            ),
            "meanTanimotoByRank": neighbor_by_rank,
        },
        "reconstructionAnalysis": {
            "evaluationMolecules": int(
                reconstruction["evaluation_molecules"]
            ),
            "selectionSplit": str(
                reconstruction["threshold_selection"][
                    "selection_split"
                ]
            ),
            "selectionMetric": str(
                reconstruction["threshold_selection"][
                    "selection_metric"
                ]
            ),
            "selectedThreshold": normalize_numeric_value(
                reconstruction["probability_threshold"],
                numeric_precision,
            ),
            "metrics": {
                "bitAccuracy": normalize_numeric_value(
                    reconstruction_metrics["bit_accuracy"],
                    numeric_precision,
                ),
                "precision": normalize_numeric_value(
                    reconstruction_metrics["precision"],
                    numeric_precision,
                ),
                "recall": normalize_numeric_value(
                    reconstruction_metrics["recall"],
                    numeric_precision,
                ),
                "f1Score": normalize_numeric_value(
                    reconstruction_metrics["f1_score"],
                    numeric_precision,
                ),
                "meanTanimoto": normalize_numeric_value(
                    reconstruction_metrics["mean_tanimoto"],
                    numeric_precision,
                ),
                "medianTanimoto": normalize_numeric_value(
                    reconstruction_metrics["median_tanimoto"],
                    numeric_precision,
                ),
                "exactMatchRate": normalize_numeric_value(
                    reconstruction_metrics["exact_match_rate"],
                    numeric_precision,
                ),
            },
            "referenceThreshold": {
                "threshold": normalize_numeric_value(
                    reference_evaluation["threshold"],
                    numeric_precision,
                ),
                "f1Score": normalize_numeric_value(
                    reference_metrics["f1_score"],
                    numeric_precision,
                ),
                "meanTanimoto": normalize_numeric_value(
                    reference_metrics["mean_tanimoto"],
                    numeric_precision,
                ),
            },
            "allZeroBaseline": {
                "bitAccuracy": normalize_numeric_value(
                    all_zero_metrics["bit_accuracy"],
                    numeric_precision,
                ),
                "f1Score": normalize_numeric_value(
                    all_zero_metrics["f1_score"],
                    numeric_precision,
                ),
                "meanTanimoto": normalize_numeric_value(
                    all_zero_metrics["mean_tanimoto"],
                    numeric_precision,
                ),
            },
            "thresholdSweep": threshold_sweep,
        },
        "robustnessAnalysis": {
            "runCount": int(robustness["run_count"]),
            "seeds": [
                int(seed)
                for seed in robustness["seeds"]
            ],
            "latentDimensions": [
                int(dimension)
                for dimension in robustness[
                    "latent_dimensions"
                ]
            ],
            "byLatentDimension": robustness_by_dimension,
        },
    }

def calculate_sha256(
    artifact_path: Path,
) -> str:
    """Calculate the SHA-256 checksum of one artifact."""
    digest = hashlib.sha256()

    with artifact_path.open("rb") as artifact_file:
        for chunk in iter(
            lambda: artifact_file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def create_manifest_payload(
    experiment_name: str,
    dataset_name: str,
    schema_version: int,
    molecule_payload: dict[str, Any],
    neighbor_payload: dict[str, Any],
    molecules_path: Path,
    neighbors_path: Path,
    metrics_path: Path,
) -> dict[str, Any]:
    """Describe browser artifacts and their data contract."""
    artifact_paths = {
        "molecules": molecules_path,
        "neighbors": neighbors_path,
        "metrics": metrics_path,
    }

    files = {
        artifact_name: {
            "fileName": artifact_path.name,
            "sizeBytes": artifact_path.stat().st_size,
            "sha256": calculate_sha256(artifact_path),
        }
        for artifact_name, artifact_path in artifact_paths.items()
    }

    return {
        "schemaVersion": schema_version,
        "experimentName": experiment_name,
        "dataset": {
            "name": dataset_name,
            "moleculeCount": molecule_payload[
                "dataset"
            ]["moleculeCount"],
            "splitCounts": molecule_payload[
                "dataset"
            ]["splitCounts"],
            "coordinateSystems": molecule_payload[
                "dataset"
            ]["coordinateSystems"],
            "properties": molecule_payload[
                "dataset"
            ]["properties"],
            "neighborQueryCount": neighbor_payload[
                "queryCount"
            ],
            "neighborsPerQuery": neighbor_payload[
                "neighborsPerQuery"
            ],
        },
        "files": files,
        "scientificWarnings": [
            (
                "PCA and UMAP coordinates are two-dimensional "
                "projections and do not preserve every latent-space "
                "relationship."
            ),
            (
                "UMAP region size and global separation must not be "
                "interpreted as proportional molecular distance."
            ),
            (
                "Tanimoto similarity measures Morgan-fingerprint "
                "overlap rather than complete chemical or biological "
                "similarity."
            ),
            (
                "The decoder reconstructs fingerprints and does not "
                "generate guaranteed valid molecular structures."
            ),
        ],
    }

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

    neighbor_payload = create_neighbor_payload(
        neighbor_results_path=resolve_project_path(
            project_root,
            data_config["neighbor_results_path"],
        ),
        molecule_table=molecule_table,
        schema_version=int(export_config["schema_version"]),
        neighbors_per_query=int(
            export_config["neighbors_per_query"]
        ),
        numeric_precision=int(
            export_config["coordinate_precision"]
        ),
    )

    neighbors_path = resolve_project_path(
        project_root,
        config["artifacts"]["neighbors_path"],
    )
    write_json_artifact(
        payload=neighbor_payload,
        artifact_path=neighbors_path,
    )

    metrics_payload = create_metrics_payload(
        neighbor_summary_path=resolve_project_path(
            project_root,
            data_config["neighbor_summary_path"],
        ),
        reconstruction_summary_path=resolve_project_path(
            project_root,
            data_config["reconstruction_summary_path"],
        ),
        robustness_summary_path=resolve_project_path(
            project_root,
            data_config["robustness_summary_path"],
        ),
        schema_version=int(export_config["schema_version"]),
        numeric_precision=int(
            export_config["coordinate_precision"]
        ),
    )

    metrics_path = resolve_project_path(
        project_root,
        config["artifacts"]["metrics_path"],
    )
    write_json_artifact(
        payload=metrics_payload,
        artifact_path=metrics_path,
    )

    manifest_payload = create_manifest_payload(
        experiment_name=str(config["experiment_name"]),
        dataset_name=str(export_config["dataset_name"]),
        schema_version=int(export_config["schema_version"]),
        molecule_payload=molecule_payload,
        neighbor_payload=neighbor_payload,
        molecules_path=molecules_path,
        neighbors_path=neighbors_path,
        metrics_path=metrics_path,
    )

    manifest_path = resolve_project_path(
        project_root,
        config["artifacts"]["manifest_path"],
    )
    write_json_artifact(
        payload=manifest_payload,
        artifact_path=manifest_path,
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
    print(
        f"Neighbor queries exported: "
        f"{neighbor_payload['queryCount']}"
    )
    print(f"Neighbor JSON saved to: {neighbors_path}")

    print(f"Metrics JSON saved to: {metrics_path}")
    print(f"Export manifest saved to: {manifest_path}")


if __name__ == "__main__":
    main()