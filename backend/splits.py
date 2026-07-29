
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


def create_split_indices(
    dataset_size: int,
    train_fraction: float,
    validation_fraction: float,
    test_fraction: float,
    seed: int,
) -> dict[str, np.ndarray]:
    """Create deterministic non-empty train, validation, and test indices."""
    if dataset_size < 3:
        raise ValueError(
            "At least three molecules are required for train/validation/test splits."
        )

    validate_split_fractions(
        train_fraction=train_fraction,
        validation_fraction=validation_fraction,
        test_fraction=test_fraction,
    )

    validation_size = int(dataset_size * validation_fraction)
    test_size = int(dataset_size * test_fraction)
    train_size = dataset_size - validation_size - test_size

    if min(train_size, validation_size, test_size) < 1:
        raise ValueError(
            "Each split must contain at least one molecule. "
            "Increase dataset size or adjust split fractions."
        )

    generator = np.random.default_rng(seed)
    shuffled_indices = generator.permutation(dataset_size)

    train_end = train_size
    validation_end = train_size + validation_size

    split_indices = {
        "train": shuffled_indices[:train_end],
        "validation": shuffled_indices[train_end:validation_end],
        "test": shuffled_indices[validation_end:],
    }

    validate_split_indices(split_indices, dataset_size)

    return split_indices
    

def save_split_indices(
    split_indices: dict[str, np.ndarray],
    output_path: str | Path,
) -> None:
    """Save split indices as a compressed NumPy artifact."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    np.savez_compressed(
        path,
        train=split_indices["train"],
        validation=split_indices["validation"],
        test=split_indices["test"],
    )
    
