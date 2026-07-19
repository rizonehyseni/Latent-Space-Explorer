import pandas as pd
from rdkit import Chem
import os

def load_qm9_data(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return []
    
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} rows from {file_path}")

    valid_molecules = []
    for smiles in df['smiles']:
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            valid_molecules.append(mol)

    print(f"Loaded {len(valid_molecules)} valid molecules from the dataset.")   
    return valid_molecules


if __name__ == "__main__":
    path = os.path.join("data", "qm9_sample.csv")
    mols = load_qm9_data(path)

