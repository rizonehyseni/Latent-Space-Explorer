import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from backend.analyze_latent_neighbors import (
    calculate_tanimoto_similarities,
    create_neighbor_analysis_artifacts,
    load_analysis_inputs,
    run_neighbor_analysis,
)


class LatentNeighborAnalysisTests(unittest.TestCase):
    def create_synthetic_data(
        self,
    ) -> tuple[np.ndarray, pd.DataFrame, np.ndarray]:
        """Create aligned latent vectors, metadata, and fingerprints."""
        latent_vectors = np.array(
            [
                [0.0, 0.0],
                [0.2, 0.0],
                [5.0, 5.0],
                [5.3, 5.0],
                [10.0, 10.0],
                [12.0, 12.0],
                [0.02, 0.0],
                [5.02, 5.0],
            ],
            dtype=np.float32,
        )

        metadata = pd.DataFrame(
            {
                "latent_row": list(range(8)),
                "id": [f"molecule-{index}" for index in range(8)],
                "smiles": [
                    "C",
                    "CC",
                    "O",
                    "CO",
                    "N",
                    "CN",
                    "CCC",
                    "COO",
                ],
                "split": [
                    "train",
                    "train",
                    "train",
                    "train",
                    "train",
                    "train",
                    "test",
                    "test",
                ],
            }
        )

        fingerprints = np.array(
            [
                [1, 1, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 1],
                [1, 1, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0, 0, 0],
            ],
            dtype=np.float32,
        )

        return latent_vectors, metadata, fingerprints

    def test_tanimoto_similarity_matches_known_values(self) -> None:
        query = np.array(
            [1, 1, 0, 0],
            dtype=bool,
        )
        candidates = np.array(
            [
                [1, 1, 0, 0],
                [1, 0, 1, 0],
                [0, 0, 1, 1],
            ],
            dtype=bool,
        )

        similarities = calculate_tanimoto_similarities(
            query,
            candidates,
        )

        np.testing.assert_allclose(
            similarities,
            [1.0, 1.0 / 3.0, 0.0],
        )

    def test_neighbor_analysis_is_deterministic(self) -> None:
        latent_vectors, metadata, fingerprints = (
            self.create_synthetic_data()
        )

        first_results, first_summary = run_neighbor_analysis(
            latent_vectors=latent_vectors,
            metadata=metadata,
            fingerprints=fingerprints.astype(bool),
            query_split="test",
            reference_split="train",
            distance_metric="euclidean",
            neighbors_per_query=2,
            random_neighbors_per_query=2,
            random_seed=42,
        )
        second_results, second_summary = run_neighbor_analysis(
            latent_vectors=latent_vectors,
            metadata=metadata,
            fingerprints=fingerprints.astype(bool),
            query_split="test",
            reference_split="train",
            distance_metric="euclidean",
            neighbors_per_query=2,
            random_neighbors_per_query=2,
            random_seed=42,
        )

        pd.testing.assert_frame_equal(first_results, second_results)
        self.assertEqual(first_summary, second_summary)
        self.assertEqual(len(first_results), 4)
        self.assertEqual(first_summary["query_count"], 2)
        self.assertEqual(first_summary["reference_count"], 6)
        self.assertEqual(first_summary["comparison_count"], 4)
        self.assertTrue(
            (
                first_results["query_split"] == "test"
            ).all()
        )
        self.assertTrue(
            (
                first_results["reference_split"] == "train"
            ).all()
        )
        self.assertTrue(
            first_results["tanimoto_similarity"].between(
                0.0,
                1.0,
            ).all()
        )

    def test_complete_analysis_creates_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            latent_vectors, metadata, fingerprints = (
                self.create_synthetic_data()
            )

            latent_vectors_path = root / "latent_vectors.npy"
            metadata_path = root / "latent_metadata.csv"
            fingerprints_path = root / "fingerprints.npy"
            export_manifest_path = root / "latent_manifest.json"

            np.save(latent_vectors_path, latent_vectors)
            np.save(fingerprints_path, fingerprints)
            metadata.to_csv(metadata_path, index=False)
            export_manifest_path.write_text(
                json.dumps(
                    {
                        "latent_representation": "encoder_mean_mu",
                        "checkpoint": {
                            "experiment_name": "test_model",
                            "best_epoch": 1,
                        },
                    }
                ),
                encoding="utf-8",
            )

            neighbors_path = root / "neighbors.csv"
            summary_path = root / "summary.json"
            distance_figure_path = root / "distance.png"
            baseline_figure_path = root / "baseline.png"

            summary = create_neighbor_analysis_artifacts(
                latent_vectors_path=latent_vectors_path,
                metadata_path=metadata_path,
                fingerprints_path=fingerprints_path,
                latent_export_manifest_path=export_manifest_path,
                neighbors_path=neighbors_path,
                summary_path=summary_path,
                distance_similarity_figure_path=(
                    distance_figure_path
                ),
                baseline_figure_path=baseline_figure_path,
                analysis_config={
                    "query_split": "test",
                    "reference_split": "train",
                    "latent_distance_metric": "euclidean",
                    "neighbors_per_query": 2,
                    "random_neighbors_per_query": 2,
                    "random_seed": 42,
                },
                fingerprint_config={
                    "type": "morgan",
                    "radius": 2,
                    "bits": 8,
                    "similarity_metric": "tanimoto",
                },
                visualization_config={
                    "figure_dpi": 80,
                    "point_alpha": 0.5,
                    "histogram_bins": 10,
                },
                project_root=root,
            )

            saved_results = pd.read_csv(neighbors_path)
            saved_summary = json.loads(
                summary_path.read_text(encoding="utf-8")
            )

            self.assertEqual(len(saved_results), 4)
            self.assertEqual(
                summary["analysis"],
                "latent_neighbor_tanimoto",
            )
            self.assertEqual(saved_summary["query_count"], 2)
            self.assertEqual(saved_summary["reference_count"], 6)
            self.assertTrue(distance_figure_path.is_file())
            self.assertTrue(baseline_figure_path.is_file())
            self.assertGreater(
                distance_figure_path.stat().st_size,
                0,
            )
            self.assertGreater(
                baseline_figure_path.stat().st_size,
                0,
            )

    def test_input_validation_rejects_row_count_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            latent_vectors, metadata, fingerprints = (
                self.create_synthetic_data()
            )

            latent_vectors_path = root / "latent_vectors.npy"
            metadata_path = root / "latent_metadata.csv"
            fingerprints_path = root / "fingerprints.npy"

            np.save(latent_vectors_path, latent_vectors)
            np.save(fingerprints_path, fingerprints[:-1])
            metadata.to_csv(metadata_path, index=False)

            with self.assertRaisesRegex(
                ValueError,
                "Fingerprint row count",
            ):
                load_analysis_inputs(
                    latent_vectors_path=latent_vectors_path,
                    metadata_path=metadata_path,
                    fingerprints_path=fingerprints_path,
                    expected_fingerprint_bits=8,
                )


if __name__ == "__main__":
    unittest.main()