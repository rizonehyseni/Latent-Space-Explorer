import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from backend.plot_latent_properties import (
    create_property_visualization_artifacts,
    load_projection_metadata,
    validate_projection_alignment,
)


PROPERTY_CONFIG = {
    "molecular_weight": {
        "label": "Molecular weight (Da)",
        "colormap": "viridis",
    },
    "logp": {
        "label": "LogP",
        "colormap": "viridis",
    },
    "tpsa": {
        "label": "TPSA",
        "colormap": "viridis",
    },
    "ring_count": {
        "label": "Ring count",
        "colormap": "viridis",
    },
    "num_heavy_atoms": {
        "label": "Heavy-atom count",
        "colormap": "viridis",
    },
}


class LatentPropertyVisualizationTests(unittest.TestCase):
    def create_base_metadata(self) -> pd.DataFrame:
        """Create aligned synthetic molecule metadata."""
        return pd.DataFrame(
            {
                "latent_row": list(range(8)),
                "id": [f"molecule-{index}" for index in range(8)],
                "smiles": [
                    "C",
                    "CC",
                    "CCC",
                    "CO",
                    "CN",
                    "C1CC1",
                    "CCO",
                    "CCN",
                ],
                "split": [
                    "train",
                    "train",
                    "train",
                    "train",
                    "train",
                    "validation",
                    "validation",
                    "test",
                ],
                "molecular_weight": [
                    16.0,
                    30.0,
                    44.0,
                    32.0,
                    31.0,
                    42.0,
                    46.0,
                    45.0,
                ],
                "logp": [
                    0.6,
                    1.0,
                    1.4,
                    -0.4,
                    -0.6,
                    1.1,
                    -0.1,
                    -0.3,
                ],
                "tpsa": [
                    0.0,
                    0.0,
                    0.0,
                    20.2,
                    26.0,
                    0.0,
                    20.2,
                    26.0,
                ],
                "ring_count": [0, 0, 0, 0, 0, 1, 0, 0],
                "num_heavy_atoms": [1, 2, 3, 2, 2, 3, 3, 3],
            }
        )

    def test_property_artifacts_preserve_alignment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            base_metadata = self.create_base_metadata()

            pca_metadata = base_metadata.copy()
            pca_metadata["pca_1"] = np.linspace(-2.0, 2.0, 8)
            pca_metadata["pca_2"] = np.linspace(1.0, 4.0, 8)

            umap_metadata = base_metadata.copy()
            umap_metadata["umap_1"] = np.linspace(-4.0, 4.0, 8)
            umap_metadata["umap_2"] = np.linspace(3.0, 7.0, 8)

            pca_metadata_path = root / "pca_metadata.csv"
            umap_metadata_path = root / "umap_metadata.csv"
            manifest_path = root / "property_manifest.json"
            pca_figure_path = root / "pca_properties.png"
            umap_figure_path = root / "umap_properties.png"

            pca_metadata.to_csv(pca_metadata_path, index=False)
            umap_metadata.to_csv(umap_metadata_path, index=False)

            manifest = create_property_visualization_artifacts(
                pca_metadata_path=pca_metadata_path,
                umap_metadata_path=umap_metadata_path,
                manifest_path=manifest_path,
                pca_figure_path=pca_figure_path,
                umap_figure_path=umap_figure_path,
                property_config=PROPERTY_CONFIG,
                visualization_config={
                    "lower_quantile": 0.01,
                    "upper_quantile": 0.99,
                    "point_size": 8,
                    "point_alpha": 0.7,
                    "figure_dpi": 80,
                },
                project_root=root,
            )

            saved_manifest = json.loads(
                manifest_path.read_text(encoding="utf-8")
            )

            self.assertTrue(pca_figure_path.is_file())
            self.assertTrue(umap_figure_path.is_file())
            self.assertGreater(pca_figure_path.stat().st_size, 0)
            self.assertGreater(umap_figure_path.stat().st_size, 0)
            self.assertEqual(manifest["dataset_size"], 8)
            self.assertEqual(
                list(manifest["properties"]),
                list(PROPERTY_CONFIG),
            )
            self.assertEqual(
                saved_manifest["split_sizes"],
                {
                    "train": 5,
                    "validation": 2,
                    "test": 1,
                },
            )

            for property_name in PROPERTY_CONFIG:
                statistics = saved_manifest["properties"][property_name]
                self.assertIn("minimum", statistics)
                self.assertIn("maximum", statistics)
                self.assertIn("color_minimum", statistics)
                self.assertIn("color_maximum", statistics)
                self.assertLess(
                    statistics["color_minimum"],
                    statistics["color_maximum"],
                )

    def test_projection_alignment_rejects_changed_molecule_order(
        self,
    ) -> None:
        base_metadata = self.create_base_metadata()

        pca_metadata = base_metadata.copy()
        pca_metadata["pca_1"] = np.linspace(-1.0, 1.0, 8)
        pca_metadata["pca_2"] = np.linspace(1.0, 2.0, 8)

        umap_metadata = base_metadata.copy()
        umap_metadata["umap_1"] = np.linspace(-2.0, 2.0, 8)
        umap_metadata["umap_2"] = np.linspace(2.0, 3.0, 8)
        umap_metadata.loc[0, "id"] = "different-molecule"

        with self.assertRaisesRegex(
            ValueError,
            "misaligned in column 'id'",
        ):
            validate_projection_alignment(
                pca_metadata=pca_metadata,
                umap_metadata=umap_metadata,
                property_columns=tuple(PROPERTY_CONFIG),
            )

    def test_metadata_rejects_non_finite_property_values(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            metadata = self.create_base_metadata()
            metadata["pca_1"] = np.linspace(-1.0, 1.0, 8)
            metadata["pca_2"] = np.linspace(1.0, 2.0, 8)
            metadata.loc[3, "logp"] = np.nan

            metadata_path = root / "invalid_metadata.csv"
            metadata.to_csv(metadata_path, index=False)

            with self.assertRaisesRegex(
                ValueError,
                "non-finite values",
            ):
                load_projection_metadata(
                    metadata_path=metadata_path,
                    coordinate_columns=("pca_1", "pca_2"),
                    property_columns=tuple(PROPERTY_CONFIG),
                )


if __name__ == "__main__":
    unittest.main()