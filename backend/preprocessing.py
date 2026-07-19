from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs
from rdkit.Chem import Crippen, Descriptors, Lipinski, rdMolDescriptors

from backend.data_handler import load_smiles_csv

FINGERPRINT_RADIUS = 2
FINGERPRINT_BITS = 2048


def molecule_properties(molecule: Chem.Mol) -> dict[str, float | int]:
    """Calculate molecular descriptors used for exploration and analysis."""
    return {
        "molecular_weight": round(Descriptors.MolWt(molecule), 4),
        "logp": round(Crippen.MolLogP(molecule), 4),
        "num_atoms": molecule.GetNumAtoms(),
        "num_heavy_atoms": molecule.GetNumHeavyAtoms(),
        "num_h_donors": Lipinski.NumHDonors(molecule),
        "num_h_acceptors": Lipinski.NumHAcceptors(molecule),
        "tpsa": round(rdMolDescriptors.CalcTPSA(molecule), 4),
        "ring_count": rdMolDescriptors.CalcNumRings(molecule),
    }


def morgan_fingerprint(molecule: Chem.Mol) -> np.ndarray:
    """Create a fixed-size Morgan fingerprint for a molecule."""
    bit_vector = rdMolDescriptors.GetMorganFingerprintAsBitVect(
        molecule,
        radius=FINGERPRINT_RADIUS,
        nBits=FINGERPRINT_BITS,
    )

    fingerprint = np.zeros((FINGERPRINT_BITS,), dtype=np.float32)
    DataStructs.ConvertToNumpyArray(bit_vector, fingerprint)
    return fingerprint


def preprocess_dataset(
    input_path: str | Path,
    output_directory: str | Path,
) -> tuple[pd.DataFrame, np.ndarray, int]:
    """
    Validate molecules, calculate descriptors, and save ML-ready artifacts.

    Returns:
        metadata, fingerprints, rejected_molecules
    """
    source_dataframe = load_smiles_csv(input_path)
    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)

    metadata_rows: list[dict] = []
    fingerprints: list[np.ndarray] = []
    rejected_molecules = 0

    for source_index, row in source_dataframe.iterrows():
        smiles = str(row["smiles"]).strip()
        molecule = Chem.MolFromSmiles(smiles)

        if molecule is None:
            rejected_molecules += 1
            continue

        properties = molecule_properties(molecule)

        metadata_rows.append(
            {
                "source_index": source_index,
                "id": row["id"] if "id" in source_dataframe.columns else source_index,
                "smiles": Chem.MolToSmiles(molecule, canonical=True),
                **properties,
                **({"gap": row["gap"]} if "gap" in source_dataframe.columns else {}),
            }
        )

        fingerprints.append(morgan_fingerprint(molecule))

    if not metadata_rows:
        raise ValueError("No valid molecules found in the dataset.")

    metadata = pd.DataFrame(metadata_rows)
    fingerprint_matrix = np.vstack(fingerprints)

    metadata.to_csv(output_path / "molecules_metadata.csv", index=False)
    np.save(output_path / "morgan_fingerprints.npy", fingerprint_matrix)

    return metadata, fingerprint_matrix, rejected_molecules