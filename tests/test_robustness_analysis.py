import unittest
import json
import tempfile
from pathlib import Path

from backend.run_robustness_analysis import (
    create_experiment_grid,
    train_robustness_run,
)

class RobustnessAnalysisTests(unittest.TestCase):
    def test_experiment_grid_contains_all_combinations(self) -> None:
        config = {
            "seeds": [7, 42],
            "model": {
                "latent_dimensions": [8, 16],
            },
        }

        grid = create_experiment_grid(config)

        self.assertEqual(
            grid,
            [
                {"seed": 7, "latent_dim": 8},
                {"seed": 42, "latent_dim": 8},
                {"seed": 7, "latent_dim": 16},
                {"seed": 42, "latent_dim": 16},
            ],
        )

    def test_duplicate_seeds_are_rejected(self) -> None:
        config = {
            "seeds": [42, 42],
            "model": {
                "latent_dimensions": [16],
            },
        }

        with self.assertRaisesRegex(ValueError, "Seeds must be unique"):
            create_experiment_grid(config)

    def test_nonpositive_latent_dimension_is_rejected(self) -> None:
        config = {
            "seeds": [42],
            "model": {
                "latent_dimensions": [0],
            },
        }

        with self.assertRaisesRegex(
            ValueError,
            "Latent dimensions must be positive",
        ):
            create_experiment_grid(config)

                    
    def test_run_name_is_stable(self) -> None:
        from backend.run_robustness_analysis import create_run_name

        self.assertEqual(
            create_run_name(seed=42, latent_dim=16),
            "latent_16_seed_42",
        )
    def test_completed_run_is_loaded_without_retraining(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_root = Path(temporary_directory)
            checkpoint_directory = project_root / "checkpoints"
            results_directory = project_root / "results"

            checkpoint_directory.mkdir()
            results_directory.mkdir()

            checkpoint_path = (
                checkpoint_directory / "latent_16_seed_42.pt"
            )
            results_path = (
                results_directory / "latent_16_seed_42.json"
            )

            checkpoint_path.write_bytes(b"completed")
            results_path.write_text(
                json.dumps(
                    {
                        "run_name": "latent_16_seed_42",
                        "seed": 42,
                        "latent_dim": 16,
                    }
                ),
                encoding="utf-8",
            )

            result = train_robustness_run(
                project_root=project_root,
                config={
                    "artifacts": {
                        "checkpoint_directory": "checkpoints",
                        "run_results_directory": "results",
                    }
                },
                run={
                    "seed": 42,
                    "latent_dim": 16,
                },
            )

            self.assertEqual(
                result["run_name"],
                "latent_16_seed_42",
            )
        

if __name__ == "__main__":
    unittest.main()