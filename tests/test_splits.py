import unittest

import numpy as np

from backend.splits import create_split_indices


class SplitUtilityTests(unittest.TestCase):
    def test_splits_are_deterministic(self) -> None:
        first_splits = create_split_indices(
            dataset_size=100,
            train_fraction=0.8,
            validation_fraction=0.1,
            test_fraction=0.1,
            seed=42,
        )
        second_splits = create_split_indices(
            dataset_size=100,
            train_fraction=0.8,
            validation_fraction=0.1,
            test_fraction=0.1,
            seed=42,
        )

        for split_name in first_splits:
            np.testing.assert_array_equal(
                first_splits[split_name],
                second_splits[split_name],
            )

    def test_split_sizes_match_requested_fractions(self) -> None:
        splits = create_split_indices(
            dataset_size=10000,
            train_fraction=0.8,
            validation_fraction=0.1,
            test_fraction=0.1,
            seed=42,
        )

        self.assertEqual(len(splits["train"]), 8000)
        self.assertEqual(len(splits["validation"]), 1000)
        self.assertEqual(len(splits["test"]), 1000)

    def test_splits_do_not_overlap(self) -> None:
        splits = create_split_indices(
            dataset_size=100,
            train_fraction=0.8,
            validation_fraction=0.1,
            test_fraction=0.1,
            seed=42,
        )

        combined = np.concatenate(list(splits.values()))

        self.assertEqual(len(combined), 100)
        self.assertEqual(len(np.unique(combined)), 100)


if __name__ == "__main__":
    unittest.main()