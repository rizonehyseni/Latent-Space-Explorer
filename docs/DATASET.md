# Dataset Documentation

## Current development dataset

The repository includes:

```text
data/qm9_sample.csv
```
This three-molecule sample exists only to verify CSV ingestion, RDKit preprocessing, Fingerprint VAE training, validation, and checkpoint generation.

It must not be used for scientific model evaluation.

## QM9 subset used for baseline experiments

The retained experiments use a deterministic 10,000-molecule subset of QM9.

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
    A[("QM9 source archive<br/>qm9.tar.gz")] --> B["Download and extract"]
    B --> C[("qm9.sdf<br/>molecular structures")]
    B --> D[("qm9.sdf.csv<br/>property table")]

    C --> E["RDKit parsing<br/>and sanitization"]
    E --> F{"Valid molecule?"}
    F -->|No| G["Record rejection"]
    F -->|Yes| H["Create canonical SMILES"]

    D --> I["Read molecule ID<br/>and HOMO-LUMO gap"]
    H --> J["Join structures<br/>with property rows"]
    I --> J
    J --> K["Seeded selection<br/>10,000 molecules"]
    K --> L[("qm9_subset.csv")]
    K --> M[("Provenance manifest<br/>SHA-256, seed, counts")]

    classDef source fill:#e8eef3,stroke:#526777,color:#17212b,stroke-width:1.5px
    classDef process fill:#e8f1ec,stroke:#4d6f5a,color:#18231c,stroke-width:1.5px
    classDef decision fill:#f5eedf,stroke:#8a6d3b,color:#2a2112,stroke-width:1.5px
    classDef rejected fill:#f5e5e3,stroke:#9a554d,color:#321816,stroke-width:1.5px
    classDef artifact fill:#ede9f5,stroke:#6b5a83,color:#211a2b,stroke-width:1.5px

    class A,C,D source
    class B,E,H,I,J,K process
    class F decision
    class G rejected
    class L,M artifact
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

The generated subset was subsequently used for fingerprint preprocessing, deterministic train/validation/test splitting, Fingerprint VAE training, latent-space analyses, and held-out evaluation.

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
## Dataset pipeline status

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
