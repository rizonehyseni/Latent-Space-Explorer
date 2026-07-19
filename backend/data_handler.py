from pathlib import Path
import pandas as pd


def load_smiles_csv(file_path: str | Path) -> pd.DataFrame:

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    dataframe = pd.read_csv(path)

    if 'smiles' not in dataframe.columns:
        raise ValueError("The CSV file must contain a 'smiles' column.")
    return dataframe


