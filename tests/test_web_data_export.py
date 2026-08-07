import tempfile
import unittest
from pathlib import Path
import json

import pandas as pd

from backend.export_web_data import (
    calculate_sha256,
    create_aligned_molecule_table,
    create_manifest_payload,
    create_metrics_payload,
    create_molecule_payload,
    create_neighbor_payload,
)

class WebDataExportTests(unittest.TestCase):
    def create_metadata(
        self,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        shared_data = {
            "latent_row": [0, 1],
            "source_index": [10, 11],
            "id": ["molecule-10", "molecule-11"],
            "smiles": ["C", "CC"],
            "split": ["train", "test"],
            "molecular_weight": [16.043, 30.070],
            "logp": [0.6361, 1.0262],
            "tpsa": [0.0, 0.0],
            "ring_count": [0, 0],
            "num_heavy_atoms": [1, 2],
            "gap": [0.5, 0.4],
        }

        pca_metadata = pd.DataFrame(
            {
                **shared_data,
                "pca_1": [0.1, 0.2],
                "pca_2": [0.3, 0.4],
            }
        )
        umap_metadata = pd.DataFrame(
            {
                **shared_data,
                "umap_1": [1.1, 1.2],
                "umap_2": [1.3, 1.4],
            }
        )

        return pca_metadata, umap_metadata

    def test_projection_metadata_is_aligned(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            pca_path = root / "pca.csv"
            umap_path = root / "umap.csv"

            pca_metadata, umap_metadata = self.create_metadata()
            pca_metadata.to_csv(pca_path, index=False)
            umap_metadata.to_csv(umap_path, index=False)

            molecule_table = create_aligned_molecule_table(
                pca_metadata_path=pca_path,
                umap_metadata_path=umap_path,
                property_columns=[
                    "molecular_weight",
                    "logp",
                    "tpsa",
                    "ring_count",
                    "num_heavy_atoms",
                    "gap",
                ],
            )

            self.assertEqual(len(molecule_table), 2)
            self.assertEqual(
                molecule_table["id"].tolist(),
                ["molecule-10", "molecule-11"],
            )
            self.assertEqual(
                molecule_table["pca_1"].tolist(),
                [0.1, 0.2],
            )
            self.assertEqual(
                molecule_table["umap_2"].tolist(),
                [1.3, 1.4],
            )

    def test_misaligned_metadata_is_rejected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            pca_path = root / "pca.csv"
            umap_path = root / "umap.csv"

            pca_metadata, umap_metadata = self.create_metadata()
            umap_metadata.loc[1, "id"] = "wrong-id"

            pca_metadata.to_csv(pca_path, index=False)
            umap_metadata.to_csv(umap_path, index=False)

            with self.assertRaisesRegex(
                ValueError,
                "not aligned for column: id",
            ):
                create_aligned_molecule_table(
                    pca_metadata_path=pca_path,
                    umap_metadata_path=umap_path,
                    property_columns=[
                        "molecular_weight",
                        "logp",
                        "tpsa",
                        "ring_count",
                        "num_heavy_atoms",
                        "gap",
                    ],
                )

    def test_duplicate_molecule_ids_are_rejected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            pca_path = root / "pca.csv"
            umap_path = root / "umap.csv"

            pca_metadata, umap_metadata = self.create_metadata()
            pca_metadata.loc[1, "id"] = "molecule-10"

            pca_metadata.to_csv(pca_path, index=False)
            umap_metadata.to_csv(umap_path, index=False)

            with self.assertRaisesRegex(
                ValueError,
                "duplicate molecule IDs",
            ):
                create_aligned_molecule_table(
                    pca_metadata_path=pca_path,
                    umap_metadata_path=umap_path,
                    property_columns=[
                        "molecular_weight",
                        "logp",
                        "tpsa",
                        "ring_count",
                        "num_heavy_atoms",
                        "gap",
                    ],
                )

    def test_molecule_payload_matches_browser_contract(
        self,
    ) -> None:
        pca_metadata, umap_metadata = self.create_metadata()

        molecule_table = pca_metadata.copy()
        molecule_table["umap_1"] = umap_metadata["umap_1"]
        molecule_table["umap_2"] = umap_metadata["umap_2"]

        payload = create_molecule_payload(
            molecule_table=molecule_table,
            experiment_name="test_web_export",
            dataset_name="QM9",
            schema_version=1,
            coordinate_precision=3,
            property_precision=2,
            property_columns=[
                "molecular_weight",
                "logp",
                "tpsa",
                "ring_count",
                "num_heavy_atoms",
                "gap",
            ],
        )

        self.assertEqual(payload["schemaVersion"], 1)
        self.assertEqual(payload["dataset"]["moleculeCount"], 2)
        self.assertEqual(
            payload["dataset"]["splitCounts"],
            {
                "train": 1,
                "validation": 0,
                "test": 1,
            },
        )

        first_molecule = payload["molecules"][0]

        self.assertEqual(first_molecule["id"], "molecule-10")
        self.assertEqual(
            first_molecule["coordinates"]["pca"],
            [0.1, 0.3],
        )
        self.assertEqual(
            first_molecule["coordinates"]["umap"],
            [1.1, 1.3],
        )
        self.assertEqual(
            first_molecule["properties"]["molecular_weight"],
            16.04,
        )
        self.assertEqual(
            first_molecule["properties"]["ring_count"],
            0,
        )      

    def test_neighbor_payload_matches_browser_contract(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            neighbor_path = root / "neighbors.csv"

            pca_metadata, umap_metadata = self.create_metadata()
            molecule_table = pca_metadata.copy()
            molecule_table["umap_1"] = umap_metadata["umap_1"]
            molecule_table["umap_2"] = umap_metadata["umap_2"]

            neighbor_results = pd.DataFrame(
                {
                    "query_latent_row": [1],
                    "query_id": ["molecule-11"],
                    "query_split": ["test"],
                    "neighbor_rank": [1],
                    "neighbor_latent_row": [0],
                    "neighbor_id": ["molecule-10"],
                    "reference_split": ["train"],
                    "latent_distance": [0.1234567],
                    "tanimoto_similarity": [0.5],
                }
            )
            neighbor_results.to_csv(
                neighbor_path,
                index=False,
            )

            payload = create_neighbor_payload(
                neighbor_results_path=neighbor_path,
                molecule_table=molecule_table,
                schema_version=1,
                neighbors_per_query=1,
                numeric_precision=4,
            )

            self.assertEqual(payload["queryCount"], 1)
            self.assertEqual(payload["neighborsPerQuery"], 1)

            query = payload["queries"]["molecule-11"]
            self.assertEqual(query["queryRow"], 1)
            self.assertEqual(
                query["neighbors"],
                [
                    {
                        "rank": 1,
                        "row": 0,
                        "id": "molecule-10",
                        "latentDistance": 0.1235,
                        "tanimoto": 0.5,
                    }
                ],
            )                  

    def test_metrics_payload_contains_scientific_summaries(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            neighbor_path = root / "neighbor.json"
            reconstruction_path = root / "reconstruction.json"
            robustness_path = root / "robustness.json"

            neighbor_path.write_text(
                json.dumps(
                    {
                        "query_count": 2,
                        "reference_count": 4,
                        "neighbors_per_query": 1,
                        "latent_distance_metric": "euclidean",
                        "nearest_neighbor_tanimoto": {
                            "mean": 0.3,
                            "median": 0.25,
                        },
                        "random_baseline_tanimoto": {
                            "mean": 0.1,
                        },
                        "mean_tanimoto_improvement": 0.2,
                        "nearest_beats_paired_random_fraction": 0.9,
                        "latent_distance_tanimoto_pearson": -0.1,
                        "latent_distance_tanimoto_spearman": -0.2,
                        "mean_tanimoto_by_rank": {
                            "1": 0.3,
                        },
                    }
                ),
                encoding="utf-8",
            )

            reconstruction_path.write_text(
                json.dumps(
                    {
                        "evaluation_molecules": 2,
                        "probability_threshold": 0.25,
                        "threshold_selection": {
                            "selection_split": "validation",
                            "selection_metric": "mean_tanimoto",
                            "sweep": [
                                {
                                    "threshold": 0.25,
                                    "precision": 0.6,
                                    "recall": 0.4,
                                    "f1_score": 0.48,
                                    "mean_tanimoto": 0.33,
                                }
                            ],
                        },
                        "model_metrics": {
                            "bit_accuracy": 0.99,
                            "precision": 0.6,
                            "recall": 0.4,
                            "f1_score": 0.48,
                            "mean_tanimoto": 0.33,
                            "median_tanimoto": 0.32,
                            "exact_match_rate": 0.0,
                        },
                        "reference_threshold_evaluation": {
                            "threshold": 0.5,
                            "model_metrics": {
                                "f1_score": 0.44,
                                "mean_tanimoto": 0.29,
                            },
                        },
                        "all_zero_baseline": {
                            "bit_accuracy": 0.98,
                            "f1_score": 0.0,
                            "mean_tanimoto": 0.0,
                        },
                    }
                ),
                encoding="utf-8",
            )

            statistic = {
                "mean": 1.0,
                "standard_deviation": 0.1,
                "minimum": 0.9,
                "maximum": 1.1,
            }

            robustness_path.write_text(
                json.dumps(
                    {
                        "run_count": 1,
                        "seeds": [42],
                        "latent_dimensions": [16],
                        "aggregate_by_latent_dimension": {
                            "16": {
                                "run_count": 1,
                                "test_loss": statistic,
                                "f1_score": statistic,
                                "mean_tanimoto": statistic,
                                "selected_threshold": statistic,
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )

            payload = create_metrics_payload(
                neighbor_summary_path=neighbor_path,
                reconstruction_summary_path=reconstruction_path,
                robustness_summary_path=robustness_path,
                schema_version=1,
                numeric_precision=4,
            )

            self.assertEqual(payload["schemaVersion"], 1)
            self.assertEqual(
                payload["neighborAnalysis"][
                    "meanNeighborTanimoto"
                ],
                0.3,
            )
            self.assertEqual(
                payload["reconstructionAnalysis"][
                    "selectedThreshold"
                ],
                0.25,
            )
            self.assertEqual(
                len(
                    payload["reconstructionAnalysis"][
                        "thresholdSweep"
                    ]
                ),
                1,
            )
            self.assertEqual(
                payload["robustnessAnalysis"]["runCount"],
                1,
            )

    def test_manifest_records_artifact_checksums(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            molecules_path = root / "molecules.json"
            neighbors_path = root / "neighbors.json"
            metrics_path = root / "metrics.json"

            molecules_path.write_text(
                '{"molecules":[]}',
                encoding="utf-8",
            )
            neighbors_path.write_text(
                '{"queries":{}}',
                encoding="utf-8",
            )
            metrics_path.write_text(
                '{"metrics":{}}',
                encoding="utf-8",
            )

            molecule_payload = {
                "dataset": {
                    "moleculeCount": 2,
                    "splitCounts": {
                        "train": 1,
                        "validation": 0,
                        "test": 1,
                    },
                    "coordinateSystems": ["pca", "umap"],
                    "properties": ["molecular_weight"],
                }
            }
            neighbor_payload = {
                "queryCount": 1,
                "neighborsPerQuery": 1,
            }

            manifest = create_manifest_payload(
                experiment_name="test_export",
                dataset_name="QM9",
                schema_version=1,
                molecule_payload=molecule_payload,
                neighbor_payload=neighbor_payload,
                molecules_path=molecules_path,
                neighbors_path=neighbors_path,
                metrics_path=metrics_path,
            )

            self.assertEqual(
                manifest["dataset"]["moleculeCount"],
                2,
            )
            self.assertEqual(
                manifest["files"]["molecules"]["fileName"],
                "molecules.json",
            )
            self.assertEqual(
                manifest["files"]["molecules"]["sha256"],
                calculate_sha256(molecules_path),
            )
            self.assertEqual(
                len(manifest["files"]["molecules"]["sha256"]),
                64,
            )
            self.assertGreater(
                len(manifest["scientificWarnings"]),
                0,
            )

if __name__ == "__main__":
    unittest.main()