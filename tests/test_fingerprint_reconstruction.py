import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from backend.evaluate_fingerprint_reconstruction import (
    calculate_binary_cross_entropy,
    calculate_prediction_metrics,
    create_reconstruction_artifacts,
    reconstruct_probabilities,
)
from backend.model import MolecularVAE


class FingerprintReconstructionTests(unittest.TestCase):
    def test_binary_metrics_match_known_values(self) -> None:
        true_fingerprints = np.array(
            [
                [1, 1, 0, 0],
                [1, 0, 1, 0],
            ],
            dtype=np.float32,
        )
        predicted_fingerprints = np.array(
            [
                [1, 0, 0, 0],
                [1, 1, 0, 0],
            ],
            dtype=bool,
        )

        aggregate, per_molecule = calculate_prediction_metrics(
            true_fingerprints=true_fingerprints,
            predicted_fingerprints=predicted_fingerprints,
        )

        self.assertAlmostEqual(
            aggregate["bit_accuracy"],
            5.0 / 8.0,
        )
        self.assertAlmostEqual(
            aggregate["precision"],
            2.0 / 3.0,
        )
        self.assertAlmostEqual(
            aggregate["recall"],
            2.0 / 4.0,
        )
        self.assertAlmostEqual(
            aggregate["f1_score"],
            4.0 / 7.0,
        )
        self.assertAlmostEqual(
            aggregate["mean_tanimoto"],
            (0.5 + 1.0 / 3.0) / 2.0,
        )
        np.testing.assert_allclose(
            per_molecule["tanimoto_similarity"],
            [0.5, 1.0 / 3.0],
        )
        self.assertEqual(
            aggregate["confusion_counts"],
            {
                "true_positive": 2,
                "true_negative": 3,
                "false_positive": 1,
                "false_negative": 2,
            },
        )

    def test_all_zero_baseline_does_not_receive_sparse_credit(
        self,
    ) -> None:
        true_fingerprints = np.array(
            [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
            ],
            dtype=np.float32,
        )
        zero_predictions = np.zeros_like(
            true_fingerprints,
            dtype=bool,
        )

        aggregate, _ = calculate_prediction_metrics(
            true_fingerprints=true_fingerprints,
            predicted_fingerprints=zero_predictions,
        )

        self.assertEqual(aggregate["precision"], 0.0)
        self.assertEqual(aggregate["recall"], 0.0)
        self.assertEqual(aggregate["f1_score"], 0.0)
        self.assertEqual(aggregate["mean_tanimoto"], 0.0)
        self.assertEqual(aggregate["bit_accuracy"], 0.75)

    def test_deterministic_latent_reconstruction_is_repeatable(
        self,
    ) -> None:
        torch.manual_seed(42)
        model = MolecularVAE(
            input_dim=4,
            hidden_dim=8,
            latent_dim=2,
        )
        model.eval()

        fingerprints = np.array(
            [
                [1, 0, 1, 0],
                [0, 1, 0, 1],
            ],
            dtype=np.float32,
        )

        first_probabilities = reconstruct_probabilities(
            model=model,
            fingerprints=fingerprints,
            batch_size=1,
            device=torch.device("cpu"),
        )
        second_probabilities = reconstruct_probabilities(
            model=model,
            fingerprints=fingerprints,
            batch_size=2,
            device=torch.device("cpu"),
        )

        np.testing.assert_allclose(
            first_probabilities,
            second_probabilities,
            rtol=1e-6,
            atol=1e-6,
        )
        self.assertTrue(
            np.logical_and(
                first_probabilities >= 0.0,
                first_probabilities <= 1.0,
            ).all()
        )

    def test_binary_cross_entropy_is_finite(self) -> None:
        true_fingerprints = np.array(
            [[1, 0, 1, 0]],
            dtype=np.float32,
        )
        probabilities = np.array(
            [[1.0, 0.0, 0.75, 0.25]],
            dtype=np.float32,
        )

        losses = calculate_binary_cross_entropy(
            true_fingerprints=true_fingerprints,
            probabilities=probabilities,
        )

        self.assertEqual(losses.shape, (1,))
        self.assertTrue(np.isfinite(losses).all())
        self.assertGreaterEqual(losses[0], 0.0)

    def test_complete_evaluation_creates_aligned_artifacts(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)

            fingerprints = np.array(
                [
                    [1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1],
                    [1, 1, 0, 0],
                    [0, 0, 1, 1],
                ],
                dtype=np.float32,
            )
            metadata = pd.DataFrame(
                {
                    "source_index": list(range(6)),
                    "id": [
                        f"molecule-{index}"
                        for index in range(6)
                    ],
                    "smiles": [
                        "C",
                        "CC",
                        "O",
                        "N",
                        "CO",
                        "CN",
                    ],
                }
            )

            fingerprints_path = root / "fingerprints.npy"
            metadata_path = root / "metadata.csv"
            split_indices_path = root / "splits.npz"
            checkpoint_path = root / "model.pt"

            np.save(fingerprints_path, fingerprints)
            metadata.to_csv(metadata_path, index=False)
            np.savez(
                split_indices_path,
                train=np.array([0, 1, 2]),
                validation=np.array([3]),
                test=np.array([4, 5]),
            )

            model = MolecularVAE(
                input_dim=4,
                hidden_dim=8,
                latent_dim=2,
            )

            for parameter in model.parameters():
                torch.nn.init.constant_(parameter, 0.0)

            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "experiment_name": "test_model",
                    "model_config": {
                        "input_dim": 4,
                        "hidden_dim": 8,
                        "latent_dim": 2,
                    },
                    "best_epoch": 1,
                    "best_validation_loss": 1.0,
                },
                checkpoint_path,
            )

            per_molecule_path = root / "per_molecule.csv"
            summary_path = root / "summary.json"
            metrics_figure_path = root / "metrics.png"
            tanimoto_figure_path = root / "tanimoto.png"

            summary = create_reconstruction_artifacts(
                fingerprints_path=fingerprints_path,
                metadata_path=metadata_path,
                split_indices_path=split_indices_path,
                checkpoint_path=checkpoint_path,
                per_molecule_path=per_molecule_path,
                summary_path=summary_path,
                metrics_figure_path=metrics_figure_path,
                tanimoto_figure_path=tanimoto_figure_path,
                evaluation_config={
                    "split": "test",
                    "validation_split": "validation",
                    "batch_size": 2,
                    "reference_threshold": 0.5,
                    "device": "cpu",
                    "deterministic_latent": "encoder_mean_mu",
                },
                threshold_selection_config={
                    "metric": "mean_tanimoto",
                    "minimum": 0.05,
                    "maximum": 0.50,
                    "step": 0.025,
                },
                metrics_config={
                    "bit_accuracy": True,
                    "precision": True,
                    "recall": True,
                    "f1_score": True,
                    "exact_match_rate": True,
                    "per_molecule_tanimoto": True,
                },
                baseline_config={
                    "all_zero_fingerprint": True,
                },
                visualization_config={
                    "figure_dpi": 80,
                    "histogram_bins": 10,
                },
                project_root=root,
            )

            per_molecule = pd.read_csv(per_molecule_path)
            saved_summary = json.loads(
                summary_path.read_text(encoding="utf-8")
            )

            self.assertEqual(len(per_molecule), 2)
            self.assertEqual(
                per_molecule["dataset_index"].tolist(),
                [4, 5],
            )
            self.assertEqual(
                per_molecule["id"].tolist(),
                ["molecule-4", "molecule-5"],
            )
            self.assertTrue(
                (
                    per_molecule["split"] == "test"
                ).all()
            )
            self.assertEqual(
                summary["evaluation_molecules"],
                2,
            )
            self.assertEqual(
                summary["threshold_selection"]["selection_split"],
                "validation",
            )
            self.assertEqual(
                summary["threshold_selection"]["selection_metric"],
                "mean_tanimoto",
            )
            self.assertEqual(
                summary["probability_threshold"],
                0.05,
            )
            self.assertEqual(
                len(summary["threshold_selection"]["sweep"]),
                19,
            )
            self.assertEqual(
                saved_summary["analysis"],
                "fingerprint_reconstruction_evaluation",
            )
            self.assertTrue(metrics_figure_path.is_file())
            self.assertTrue(tanimoto_figure_path.is_file())
            self.assertGreater(
                metrics_figure_path.stat().st_size,
                0,
            )
            self.assertGreater(
                tanimoto_figure_path.stat().st_size,
                0,
            )


if __name__ == "__main__":
    unittest.main()