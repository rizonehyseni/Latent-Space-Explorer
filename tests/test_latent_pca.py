import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from backend.plot_latent_pca import create_pca_artifacts


class LatentPcaTests(unittest.TestCase):
    def test_pca_artifacts_preserve_metadata_alignment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)

            latent_vectors = np.array(
                [
                    [0.0, 0.0, 0.0],
                    [1.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0],
                    [1.0, 1.0, 0.0],
                    [2.0, 2.0, 1.0],
                ],
                dtype=np.float32,
            )
            latent_vectors_path = root / "latent_vectors.npy"
            np.save(latent_vectors_path, latent_vectors)

            latent_metadata = pd.DataFrame(
                {
                    "latent_row": [0, 1, 2, 3, 4],
                    "id": ["a", "b", "c", "d", "e"],
                    "smiles": ["C", "CC", "CO", "CN", "O"],
                    "split": [
                        "train",
                        "train",
                        "train",
                        "validation",
                        "test",
                    ],
                }
            )
            latent_metadata_path = root / "latent_metadata.csv"
            latent_metadata.to_csv(latent_metadata_path, index=False)

            latent_export_manifest_path = root / "latent_manifest.json"
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

            coordinates_path = root / "pca_coordinates.npy"
            metadata_path = root / "pca_metadata.csv"
            manifest_path = root / "pca_manifest.json"
            figure_path = root / "pca_figure.png"

            manifest = create_pca_artifacts(
                latent_vectors_path=latent_vectors_path,
                latent_metadata_path=latent_metadata_path,
                latent_export_manifest_path=latent_export_manifest_path,
                coordinates_path=coordinates_path,
                metadata_path=metadata_path,
                manifest_path=manifest_path,
                figure_path=figure_path,
                components=2,
                fit_split="train",
                project_root=root,
            )

            coordinates = np.load(coordinates_path)
            pca_metadata = pd.read_csv(metadata_path)
            saved_manifest = json.loads(
                manifest_path.read_text(encoding="utf-8")
            )

            self.assertEqual(coordinates.shape, (5, 2))
            self.assertTrue(np.isfinite(coordinates).all())
            self.assertEqual(
                pca_metadata["id"].tolist(),
                ["a", "b", "c", "d", "e"],
            )
            self.assertEqual(
                pca_metadata["split"].tolist(),
                ["train", "train", "train", "validation", "test"],
            )
            self.assertIn("pca_1", pca_metadata.columns)
            self.assertIn("pca_2", pca_metadata.columns)
            self.assertTrue(figure_path.is_file())
            self.assertGreater(figure_path.stat().st_size, 0)
            self.assertEqual(manifest["fit_split"], "train")
            self.assertEqual(
                saved_manifest["split_sizes"],
                {"train": 3, "validation": 1, "test": 1},
            )
            self.assertEqual(
                len(saved_manifest["explained_variance_ratio"]),
                2,
            )


if __name__ == "__main__":
    unittest.main()