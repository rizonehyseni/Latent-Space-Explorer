from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset

from backend.preprocessing import FINGERPRINT_BITS


class FingerprintDataset(Dataset):
    """PyTorch dataset for preprocessed molecular Morgan fingerprints."""

    def __init__(self, fingerprint_path: str | Path) -> None:
        path = Path(fingerprint_path)

        if not path.is_file():
            raise FileNotFoundError(
                f"Fingerprint dataset was not found: {path}"
            )

        fingerprints = np.load(path)

        if fingerprints.ndim != 2:
            raise ValueError(
                "Fingerprint dataset must be a 2D matrix with shape "
                "(number_of_molecules, fingerprint_bits)."
            )

        if fingerprints.shape[1] != FINGERPRINT_BITS:
            raise ValueError(
                f"Expected {FINGERPRINT_BITS} fingerprint bits, "
                f"but found {fingerprints.shape[1]}."
            )

        if len(fingerprints) == 0:
            raise ValueError("Fingerprint dataset is empty.")

        self.fingerprints = torch.from_numpy(
            fingerprints.astype(np.float32)
        )

    def __len__(self) -> int:
        return len(self.fingerprints)

    def __getitem__(self, index: int) -> torch.Tensor:
        return self.fingerprints[index]