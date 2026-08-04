import unittest
import json
import tempfile
from pathlib import Path

from backend.run_robustness_analysis import (
    create_experiment_grid,
    create_robustness_figure,
    create_robustness_summary,
    summarize_values,
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

    def test_metric_summary_uses_sample_standard_deviation(
        self,
    ) -> None:
        summary = summarize_values([2.0, 4.0])

        self.assertEqual(summary["mean"], 3.0)
        self.assertAlmostEqual(
            summary["standard_deviation"],
            2.0 ** 0.5,
        )
        self.assertEqual(summary["minimum"], 2.0)
        self.assertEqual(summary["maximum"], 4.0)

    def test_results_are_aggregated_by_latent_dimension(
        self,
    ) -> None:
        results = []

        for seed, loss, f1, tanimoto, threshold in [
            (7, 80.0, 0.4, 0.3, 0.2),
            (42, 70.0, 0.6, 0.5, 0.3),
        ]:
            results.append(
                {
                    "run_name": f"latent_16_seed_{seed}",
                    "seed": seed,
                    "latent_dim": 16,
                    "best_epoch": 50,
                    "best_validation_loss": loss,
                    "test_metrics": {
                        "loss": loss,
                    },
                    "reconstruction_evaluation": {
                        "selected_threshold": threshold,
                        "test_metrics": {
                            "f1_score": f1,
                            "mean_tanimoto": tanimoto,
                        },
                    },
                }
            )

        summary = create_robustness_summary(
            results=results,
            config={
                "experiment_name": "test_robustness",
            },
        )

        aggregate = summary[
            "aggregate_by_latent_dimension"
        ]["16"]

        self.assertEqual(summary["run_count"], 2)
        self.assertEqual(aggregate["run_count"], 2)
        self.assertEqual(
            aggregate["test_loss"]["mean"],
            75.0,
        )
        self.assertAlmostEqual(
            aggregate["f1_score"]["mean"],
            0.5,
        )
        self.assertAlmostEqual(
            aggregate["mean_tanimoto"]["mean"],
            0.4,
        )
        self.assertAlmostEqual(
            aggregate["selected_threshold"]["mean"],
            0.25,
        )     


    def test_robustness_figure_is_created(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            figure_path = (
                Path(temporary_directory) / "robustness.png"
            )

            aggregate = {}
            for latent_dim, loss, f1, tanimoto in [
                (8, 80.0, 0.45, 0.30),
                (16, 75.0, 0.50, 0.34),
                (32, 77.0, 0.48, 0.32),
            ]:
                aggregate[str(latent_dim)] = {
                    "test_loss": {
                        "mean": loss,
                        "standard_deviation": 1.0,
                    },
                    "f1_score": {
                        "mean": f1,
                        "standard_deviation": 0.02,
                    },
                    "mean_tanimoto": {
                        "mean": tanimoto,
                        "standard_deviation": 0.01,
                    },
                }

            create_robustness_figure(
                summary={
                    "latent_dimensions": [8, 16, 32],
                    "aggregate_by_latent_dimension": aggregate,
                },
                figure_path=figure_path,
            )

            self.assertTrue(figure_path.is_file())
            self.assertGreater(
                figure_path.stat().st_size,
                0,
            )

               
        

if __name__ == "__main__":
    unittest.main()