import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from backend.export_latent_vectors import export_latent_space_artifacts
from backend.model import MolecularVAE


class LatentExportTests(unittest.TestCase):
    def test_export_preserves_row_and_split_alignment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)

            fingerprints = np.array(
                [
                    [1.0, 0.0, 1.0, 0.0],
                    [0.0, 1.0, 0.0, 1.0],
                    [1.0, 1.0, 0.0, 0.0],
                ],
                dtype=np.float32,
            )
            fingerprint_path = root / "fingerprints.npy"
            np.save(fingerprint_path, fingerprints)

            metadata = pd.DataFrame(
                {
                    "source_index": [10, 11, 12],
                    "id": ["molecule_a", "molecule_b", "molecule_c"],
                    "smiles": ["C", "CC", "CO"],
                    "molecular_weight": [16.043, 30.07, 32.042],
                }
            )
            metadata_path = root / "metadata.csv"
            metadata.to_csv(metadata_path, index=False)

            split_indices_path = root / "splits.npz"
            np.savez_compressed(
                split_indices_path,
                train=np.array([0]),
                validation=np.array([1]),
                test=np.array([2]),
            )

            model_config = {
                "input_dim": 4,
                "hidden_dim": 8,
                "latent_dim": 2,
            }
            torch.manual_seed(7)
            model = MolecularVAE(**model_config)

            checkpoint_path = root / "model.pt"
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "model_config": model_config,
                    "experiment_name": "test_export",
                    "best_epoch": 1,
                    "best_validation_loss": 1.0,
                },
                checkpoint_path,
            )

            latent_vectors_path = root / "latent_vectors.npy"
            latent_metadata_path = root / "latent_metadata.csv"
            manifest_path = root / "manifest.json"

            manifest = export_latent_space_artifacts(
                fingerprint_path=fingerprint_path,
                metadata_path=metadata_path,
                split_indices_path=split_indices_path,
                checkpoint_path=checkpoint_path,
                latent_vectors_path=latent_vectors_path,
                latent_metadata_path=latent_metadata_path,
                manifest_path=manifest_path,
                model_config=model_config,
                batch_size=2,
                device=torch.device("cpu"),
                project_root=root,
            )

            exported_vectors = np.load(latent_vectors_path)
            exported_metadata = pd.read_csv(latent_metadata_path)
            saved_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

            with torch.no_grad():
                expected_vectors, _ = model.encode(
                    torch.from_numpy(fingerprints)
                )

            np.testing.assert_allclose(
                exported_vectors,
                expected_vectors.numpy(),
            )
            self.assertEqual(exported_vectors.shape, (3, 2))
            self.assertEqual(
                exported_metadata["id"].tolist(),
                ["molecule_a", "molecule_b", "molecule_c"],
            )
            self.assertEqual(
                exported_metadata["split"].tolist(),
                ["train", "validation", "test"],
            )
            self.assertEqual(
                exported_metadata["latent_row"].tolist(),
                [0, 1, 2],
            )
            self.assertEqual(
                manifest["latent_representation"],
                "encoder_mean_mu",
            )
            self.assertEqual(
                saved_manifest["split_sizes"],
                {"train": 1, "validation": 1, "test": 1},
            )


if __name__ == "__main__":
    unittest.main()