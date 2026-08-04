import unittest

from backend.run_robustness_analysis import create_experiment_grid


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

if __name__ == "__main__":
    unittest.main()