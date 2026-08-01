import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd

from backend.plot_latent_umap import (
    create_umap_artifacts,
    fit_umap_projection,
)


class LatentUmapTests(unittest.TestCase):
    def test_umap_is_fitted_only_on_training_split(self) -> None:
        latent_vectors = np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [5.0, 5.0, 5.0],
                [9.0, 9.0, 9.0],
            ],
            dtype=np.float32,
        )
        split_labels = np.array(
            ["train", "train", "train", "validation", "test"]
        )

        projector = MagicMock()
        projector.fit.return_value = projector
        projector.transform.return_value = np.zeros(
            (len(latent_vectors), 2),
            dtype=np.float32,
        )

        with patch(
            "backend.plot_latent_umap.UMAP",
            return_value=projector,
        ):
            coordinates = fit_umap_projection(
                latent_vectors=latent_vectors,
                split_labels=split_labels,
                components=2,
                fit_split="train",
                n_neighbors=2,
                min_dist=0.1,
                metric="euclidean",
                random_state=42,
                transform_seed=42,
            )

        fitted_vectors = projector.fit.call_args.args[0]

        np.testing.assert_array_equal(
            fitted_vectors,
            latent_vectors[:3],
        )
        projector.transform.assert_called_once()
        self.assertEqual(coordinates.shape, (5, 2))

    def test_umap_artifacts_preserve_metadata_alignment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            generator = np.random.default_rng(42)

            latent_vectors = generator.normal(
                size=(16, 4)
            ).astype(np.float32)
            latent_vectors_path = root / "latent_vectors.npy"
            np.save(latent_vectors_path, latent_vectors)

            split_labels = (
                ["train"] * 12
                + ["validation"] * 2
                + ["test"] * 2
            )
            molecule_ids = [
                f"molecule-{index}"
                for index in range(len(latent_vectors))
            ]

            latent_metadata = pd.DataFrame(
                {
                    "latent_row": list(range(len(latent_vectors))),
                    "id": molecule_ids,
                    "smiles": ["C"] * len(latent_vectors),
                    "split": split_labels,
                }
            )
            latent_metadata_path = root / "latent_metadata.csv"
            latent_metadata.to_csv(
                latent_metadata_path,
                index=False,
            )

            latent_export_manifest_path = (
                root / "latent_export_manifest.json"
            )
            latent_export_manifest_path.write_text(
                json.dumps(
                    {
                        "latent_representation": "encoder_mean_mu",
                        "checkpoint": {
                            "experiment_name": "test_export",
                            "best_epoch": 1,
                        },
                    }
                ),
                encoding="utf-8",
            )

            coordinates_path = root / "umap_coordinates.npy"
            metadata_path = root / "umap_metadata.csv"
            manifest_path = root / "umap_manifest.json"
            figure_path = root / "umap_figure.png"

            manifest = create_umap_artifacts(
                latent_vectors_path=latent_vectors_path,
                latent_metadata_path=latent_metadata_path,
                latent_export_manifest_path=(
                    latent_export_manifest_path
                ),
                coordinates_path=coordinates_path,
                metadata_path=metadata_path,
                manifest_path=manifest_path,
                figure_path=figure_path,
                components=2,
                fit_split="train",
                n_neighbors=3,
                min_dist=0.1,
                metric="euclidean",
                random_state=42,
                transform_seed=42,
                project_root=root,
            )

            coordinates = np.load(coordinates_path)
            umap_metadata = pd.read_csv(metadata_path)
            saved_manifest = json.loads(
                manifest_path.read_text(encoding="utf-8")
            )

            self.assertEqual(coordinates.shape, (16, 2))
            self.assertTrue(np.isfinite(coordinates).all())
            self.assertEqual(
                umap_metadata["id"].tolist(),
                molecule_ids,
            )
            self.assertEqual(
                umap_metadata["split"].tolist(),
                split_labels,
            )
            self.assertIn("umap_1", umap_metadata.columns)
            self.assertIn("umap_2", umap_metadata.columns)
            self.assertTrue(figure_path.is_file())
            self.assertGreater(figure_path.stat().st_size, 0)
            self.assertEqual(manifest["projection_method"], "UMAP")
            self.assertEqual(manifest["fit_split"], "train")
            self.assertEqual(
                saved_manifest["split_sizes"],
                {
                    "train": 12,
                    "validation": 2,
                    "test": 2,
                },
            )
            self.assertEqual(
                saved_manifest["parameters"],
                {
                    "n_neighbors": 3,
                    "min_dist": 0.1,
                    "metric": "euclidean",
                    "random_state": 42,
                    "transform_seed": 42,
                },
            )


if __name__ == "__main__":
    unittest.main()