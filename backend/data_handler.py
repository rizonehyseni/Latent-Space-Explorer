from rdkit import Chem

def load_multiple_molecules(smiles_list):
    valid_mols = []
    for smiles in smiles_list:
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            valid_mols.append(mol)
    return valid_mols    


test_list = ["CCO","c1ccccc1","CCN"]
mols = load_multiple_molecules(test_list)
print(f"Loaded {len(mols)} valid molecules from the list.")