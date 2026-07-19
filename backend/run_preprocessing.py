from pathlib import Path

from backend.preprocessing import FINGERPRINT_BITS, preprocess_dataset


def main() -> None:
    project_root = Path(__file__).parent.parent
    input_path = project_root / "data" / "qm9_sample.csv"
    output_directory = project_root / "data" / "processed"  

    metadata, fingerprints, rejected = preprocess_dataset(
        input_path = input_path, 
        output_directory =  output_directory,
        )
    
    print("Preprocessing complete.")
    print(f"Valid molecules: {len(metadata)}")
    print(f"Rejected molecules: {rejected}")
    print(f"Fingerprint shape: {fingerprints.shape}")
    print(f"Fingerprint width: {FINGERPRINT_BITS}")
    print(f"Output directory: {output_directory}")

if __name__ == "__main__":
    main() 