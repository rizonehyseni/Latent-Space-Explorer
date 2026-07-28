"""Download and prepare a reproducible QM9 subset for later preprocessing."""

import argparse
import hashlib
import json
import tarfile
from pathlib import Path
from typing import Any
from urllib.request import urlretrieve

import pandas as pd
import yaml
from rdkit import Chem

def parse_arguments() -> argparse.Namespace:
    """Read the QM9 preparation configuration path."""
    parser = argparse.ArgumentParser(
        description="Download and prepare a deterministic QM9 subset."
    )
    parser.add_argument(
        "--config",
        default="configs/qm9_subset.yaml",
        help="Path to the QM9 preparation YAML configuration.",
    )
    return parser.parse_args()


def load_dataset_config(config_path: Path) -> dict[str, Any]:
    """Load the required QM9 subset configuration."""
    if not config_path.is_file():
        raise FileNotFoundError(
            f"Dataset configuration was not found: {config_path}"
        )

    with config_path.open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    required_sections = {"source", "subset", "output"}
    if not isinstance(config, dict):
        raise ValueError("Dataset configuration must contain a YAML mapping.")

    missing_sections = required_sections.difference(config)
    if missing_sections:
        missing = ", ".join(sorted(missing_sections))
        raise ValueError(
            f"Dataset configuration is missing required sections: {missing}"
        )

    return config

def download_archive(url: str, archive_path: Path) -> None:
    """Download the QM9 archive only when it is not already available."""
    archive_path.parent.mkdir(parents=True, exist_ok=True)

    if archive_path.is_file():
        print(f"Using existing archive: {archive_path}")
        return

    print(f"Downloading QM9 archive from: {url}")
    urlretrieve(url, archive_path)
    print(f"Downloaded archive to: {archive_path}")

def extract_archive(archive_path: Path, destination: Path) -> None:
    """Extract a tar archive after checking paths remain inside destination."""
    destination.mkdir(parents=True, exist_ok=True)

    with tarfile.open(archive_path, "r:gz") as archive:
        destination_root = destination.resolve()

        for member in archive.getmembers():
            member_path = (destination / member.name).resolve()
            if destination_root not in member_path.parents and member_path != destination_root:
                raise ValueError(
                    f"Archive member escapes the destination directory: {member.name}"
                )

        archive.extractall(destination)

    print(f"Extracted archive to: {destination}")


def find_extracted_file(directory: Path, filename: str) -> Path:
    """Find exactly one extracted source file by name."""
    matches = list(directory.rglob(filename))

    if len(matches) != 1:
        raise FileNotFoundError(
            f"Expected exactly one {filename} file in {directory}, "
            f"but found {len(matches)}."
        )

    return matches[0]


def calculate_sha256(file_path: Path) -> str:
    """Calculate the SHA-256 checksum of a source archive."""
    digest = hashlib.sha256()

    with file_path.open("rb") as source_file:
        for chunk in iter(lambda: source_file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def build_qm9_subset(
    sdf_path: Path,
    properties_path: Path,
    subset_size: int,
    seed: int,
) -> tuple[pd.DataFrame, int]:
    """Join QM9 structures and properties, then select a reproducible subset."""
    properties = pd.read_csv(properties_path)

    if "gap" not in properties.columns:
        raise ValueError("QM9 property table must contain a 'gap' column.")

    supplier = Chem.SDMolSupplier(
        str(sdf_path),
        sanitize=True,
        removeHs=True,
    )

    records: list[dict[str, object]] = []
    rejected_molecules = 0

    for source_index, molecule in enumerate(supplier):
        if molecule is None:
            rejected_molecules += 1
            continue

        if source_index >= len(properties):
            raise ValueError(
                "The SDF file contains more molecules than the property table."
            )

        property_row = properties.iloc[source_index]
        molecule_id = (
            property_row["mol_id"]
            if "mol_id" in properties.columns
            else source_index + 1
        )

        records.append(
            {
                "id": str(molecule_id),
                "smiles": Chem.MolToSmiles(molecule, canonical=True),
                "gap": float(property_row["gap"]),
            }
        )

    if len(properties) != source_index + 1:
        raise ValueError(
            "The SDF file and property table have different molecule counts."
        )

    dataset = pd.DataFrame(records)

    if subset_size <= 0:
        raise ValueError("subset.size must be greater than zero.")

    if subset_size > len(dataset):
        raise ValueError(
            f"Requested subset size {subset_size}, but only "
            f"{len(dataset)} valid molecules are available."
        )

    subset = dataset.sample(
        n=subset_size,
        random_state=seed,
    ).sort_values("id")

    return subset.reset_index(drop=True), rejected_molecules

def main() -> None:
    """Download QM9 and write a deterministic standardized CSV subset."""
    arguments = parse_arguments()
    project_root = Path(__file__).resolve().parent.parent

    config_path = Path(arguments.config)
    if not config_path.is_absolute():
        config_path = project_root / config_path

    config = load_dataset_config(config_path)

    source_config = config["source"]
    subset_config = config["subset"]
    output_config = config["output"]

    raw_directory = project_root / source_config["raw_directory"]
    archive_path = raw_directory / source_config["archive_name"]
    output_csv = project_root / output_config["dataset_csv"]
    manifest_path = project_root / output_config["manifest_json"]

    download_archive(source_config["url"], archive_path)
    extract_archive(archive_path, raw_directory)

    sdf_path = find_extracted_file(raw_directory, "qm9.sdf")
    properties_path = find_extracted_file(raw_directory, "qm9.sdf.csv")

    subset, rejected_molecules = build_qm9_subset(
        sdf_path=sdf_path,
        properties_path=properties_path,
        subset_size=int(subset_config["size"]),
        seed=int(subset_config["seed"]),
    )

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    subset.to_csv(output_csv, index=False)

    manifest = {
        "dataset_name": config.get("dataset_name", "qm9_subset"),
        "source_url": source_config["url"],
        "archive_sha256": calculate_sha256(archive_path),
        "source_sdf": str(sdf_path.relative_to(project_root)),
        "source_properties": str(properties_path.relative_to(project_root)),
        "subset_size": len(subset),
        "subset_seed": int(subset_config["seed"]),
        "rejected_molecules": rejected_molecules,
        "columns": list(subset.columns),
    }

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    print("QM9 subset preparation complete.")
    print(f"Valid subset molecules: {len(subset)}")
    print(f"Rejected molecules: {rejected_molecules}")
    print(f"Subset CSV: {output_csv}")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()