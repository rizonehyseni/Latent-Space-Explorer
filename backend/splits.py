
"""Deterministic dataset split helpers for molecular experiments."""

from math import isclose
from pathlib import Path

import numpy as np


def validate_split_fractions(
    train_fraction: float,
    validation_fraction: float,
    test_fraction: float,
) -> None:
    """Validate that split fractions are positive and sum to one."""
    fractions = {
        "train_fraction": train_fraction,
        "validation_fraction": validation_fraction,
        "test_fraction": test_fraction,
    }

    for name, fraction in fractions.items():
        if fraction <= 0:
            raise ValueError(f"{name} must be greater than zero.")

    if not isclose(sum(fractions.values()), 1.0, rel_tol=0.0, abs_tol=1e-9):
        raise ValueError("Split fractions must sum to 1.0.")


def validate_split_indices(
    split_indices: dict[str, np.ndarray],
    dataset_size: int,
) -> None:
    """Ensure splits are non-overlapping and cover every dataset row."""
    expected_names = {"train", "validation", "test"}

    if set(split_indices) != expected_names:
        raise ValueError(
            "Split indices must contain train, validation, and test arrays."
        )

    combined_indices = np.concatenate(list(split_indices.values()))

    if len(combined_indices) != dataset_size:
        raise ValueError("Split indices do not cover the full dataset.")

    if len(np.unique(combined_indices)) != dataset_size:
        raise ValueError("Split indices overlap.")

    if not np.array_equal(np.sort(combined_indices), np.arange(dataset_size)):
        raise ValueError("Split indices contain invalid dataset positions.")


    