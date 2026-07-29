import json
import tempfile
import unittest
from pathlib import Path

from backend.plot_training_history import (
    load_training_history,
    plot_training_history,
)


class TrainingHistoryPlotTests(unittest.TestCase):
    def test_plot_is_created_from_valid_history(self) -> None:
        history = [
            {
                "epoch": 1.0,
                "loss": 10.0,
                "reconstruction_loss": 9.0,
                "kl_divergence": 1.0,
                "validation_loss": 11.0,
                "validation_reconstruction_loss": 10.0,
                "validation_kl_divergence": 1.0,
            },
            {
                "epoch": 2.0,
                "loss": 8.0,
                "reconstruction_loss": 7.0,
                "kl_divergence": 1.0,
                "validation_loss": 9.0,
                "validation_reconstruction_loss": 8.0,
                "validation_kl_divergence": 1.0,
            },
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = (
                Path(temporary_directory)
                / "training-curves.png"
            )

            plot_training_history(history, output_path)

            self.assertTrue(output_path.is_file())
            self.assertGreater(output_path.stat().st_size, 0)

    def test_history_loads_from_results_json(self) -> None:
        results = {
            "training_history": [
                {
                    "epoch": 1.0,
                    "loss": 10.0,
                    "reconstruction_loss": 9.0,
                    "kl_divergence": 1.0,
                    "validation_loss": 11.0,
                    "validation_reconstruction_loss": 10.0,
                    "validation_kl_divergence": 1.0,
                }
            ]
        }

        with tempfile.TemporaryDirectory() as temporary_directory:
            results_path = Path(temporary_directory) / "results.json"
            results_path.write_text(
                json.dumps(results),
                encoding="utf-8",
            )

            history = load_training_history(results_path)

            self.assertEqual(len(history), 1)
            self.assertEqual(history[0]["epoch"], 1.0)


if __name__ == "__main__":
    unittest.main()