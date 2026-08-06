import tempfile
import unittest
from pathlib import Path

import pandas as pd

from backend.export_web_data import create_aligned_molecule_table


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


if __name__ == "__main__":
    unittest.main()