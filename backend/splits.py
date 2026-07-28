
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