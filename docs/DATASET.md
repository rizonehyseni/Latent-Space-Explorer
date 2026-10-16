# Dataset Documentation

## Current development dataset

The repository includes:

```text
data/qm9_sample.csv
```
This three-molecule sample exists only to verify CSV ingestion, RDKit preprocessing, Fingerprint VAE training, validation, and checkpoint generation.

It must not be used for scientific model evaluation.

## QM9 subset for baseline experiments

The baseline experiments use a deterministic subset of QM9.

QM9 contains small organic molecules with quantum-chemical properties. The preparation workflow uses an SDF structure file and a companion CSV property table containing the HOMO-LUMO gap (`gap`).

## Source

The preparation script downloads:

```text
https://deepchemdata.s3.us-west-1.amazonaws.com/datasets/qm9.tar.gz
```

The archive is the QM9 source used by DeepChem's QM9 loader and contains:

- `qm9.sdf`
- `qm9.sdf.csv`

The original QM9 collection should be cited as:

> Ramakrishnan, R., Dral, P., Rupp, M., and von Lilienfeld, O. A. *Quantum chemistry structures and properties of 134 kilo molecules.* Scientific Data **1**, 140022 (2014).

Original collection:

```text
https://figshare.com/collections/Quantum_chemistry_structures_and_properties_of_134_kilo_molecules/978904
```

## Preparation workflow

```mermaid
flowchart TD
    A["QM9 source archive<br/>qm9.tar.gz"] --> B["Download and extract"]
    B --> C["qm9.sdf<br/>Molecular structures"]
    B --> D["qm9.sdf.csv<br/>Quantum-chemical properties"]
    C --> E["RDKit sanitization<br/>and canonical SMILES"]
    D --> F["Read molecule ID<br/>and HOMO-LUMO gap"]
    E --> G["Reject invalid molecules"]
    E --> H["Join valid structures<br/>with property rows"]
    F --> H
    H --> I["Deterministic subset<br/>10,000 molecules, seed 42"]
    I --> J["qm9_subset.csv"]
    I --> K["Provenance manifest<br/>SHA-256, seed, counts"]
```

Run:

```bash
python -m backend.prepare_qm9
```

The workflow:

- downloads the QM9 archive if it is not already present;
- extracts the SDF structures and property table;
- loads molecular structures with RDKit;
- creates canonical SMILES;
- retains molecule ID, SMILES, and HOMO-LUMO gap;
- selects a deterministic subset using the configured seed;
- writes a standardized CSV and provenance manifest.

## Configuration

The default subset configuration is stored in:

```text
configs/qm9_subset.yaml
```

Default values:

| Setting | Value |
|----------|-------|
| Subset size | 10,000 molecules |
| Random seed | 42 |
| Standardized output | `data/interim/qm9_subset.csv` |
| Provenance manifest | `data/interim/qm9_subset_manifest.json` |

## Generated artifacts

The generated data artifacts are intentionally excluded from Git:

```text
data/raw/qm9/
data/interim/qm9_subset.csv
data/interim/qm9_subset_manifest.json
```

The manifest records:

- source URL;
- SHA-256 checksum of the downloaded archive;
- source file paths;
- subset size;
- random seed;
- rejected-molecule count;
- output columns.

## Preparation run record

**Date:** 2026-07-28  
**Configuration:** `configs/qm9_subset.yaml`  
**Source archive:** `qm9.tar.gz`  
**Subset seed:** 42  
**Requested subset size:** 10,000 molecules  

### Outcome

The QM9 preparation workflow completed successfully.

| Item | Result |
| --- | --- |
| Selected standardized molecules | 10,000 |
| Rejected during RDKit SDF sanitization | 1,688 |
| Output dataset | `data/interim/qm9_subset.csv` |
| Provenance manifest | `data/interim/qm9_subset_manifest.json` |

### Interpretation

RDKit reported valence and sanitization errors for 1,688 source structures. These molecules were excluded because a valid canonical SMILES representation could not be created under the current RDKit sanitization rules.

The generated 10,000-molecule subset is suitable for the next project step: preprocessing, deterministic train/validation/test splitting, and meaningful Fingerprint VAE evaluation.

### Retained local evidence

The following generated artifacts are retained locally and excluded from Git because they can be recreated from the documented configuration:

- `data/raw/qm9/`
- `data/interim/qm9_subset.csv`
- `data/interim/qm9_subset_manifest.json`

## QM9 preprocessing and split record

**Date:** 2026-07-29  
**Input dataset:** `data/interim/qm9_subset.csv`  
**Processing configuration:** `configs/qm9_processing.yaml`  
**Fingerprint representation:** Morgan fingerprint, radius 2, 2048 bits  
**Split seed:** 42  

### Outcome

| Item | Result |
| --- | ---: |
| Input molecules | 10,000 |
| Valid processed molecules | 10,000 |
| Rejected during preprocessing | 0 |
| Training partition | 8,000 |
| Validation partition | 1,000 |
| Test partition | 1,000 |

### Generated local artifacts

```text
data/processed/qm9/molecules_metadata.csv
data/processed/qm9/morgan_fingerprints.npy
data/processed/qm9/split_indices.npz
data/processed/qm9/preparation_summary.json
```
## Current project status

The QM9 baseline dataset pipeline is complete for the first controlled experiment:

| Stage | Status |
|---|---|
| QM9 source download and provenance capture | Complete |
| RDKit structure validation and canonical SMILES generation | Complete |
| Deterministic 10,000-molecule subset creation | Complete |
| Morgan fingerprint generation | Complete |
| Deterministic train, validation, and test split creation | Complete |
| Baseline Fingerprint VAE training and held-out test evaluation | Complete |
| Deterministic latent-vector export | Complete |
| PCA, UMAP, and molecular-property analysis | Complete |
| Latent-neighbor and reconstruction evaluation | Complete |
| Multi-seed and latent-dimension robustness analysis | Complete |
| Validated browser-data export | Complete |

The processed QM9 subset contains:

| Split | Molecules |
|---|---:|
| Training | 8,000 |
| Validation | 1,000 |
| Test | 1,000 |
| Total | 10,000 |

The first QM9 Fingerprint VAE baseline was trained using this dataset. The model selected the checkpoint with the lowest validation loss and evaluated the held-out test split only after checkpoint selection.

## Current limitations


- The experiment uses a deterministic 10,000-molecule subset rather than the complete QM9 collection.
- Random train, validation, and test splits do not measure scaffold-level generalization.
- QM9 primarily represents small organic molecules and does not cover the broader diversity of drug-like chemistry.
- Morgan fingerprints discard explicit three-dimensional geometry and are not directly invertible into valid molecular structures.
- The selected subset may not preserve the complete property distribution of full QM9.
- Results should not be generalized automatically to larger molecules or other molecular datasets.

These limitations define the scope of the current controlled baseline rather than incomplete implementation work.