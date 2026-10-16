# QM9 Latent Vector Export

## Purpose

This artifact converts the selected QM9 Fingerprint VAE checkpoint into a reusable latent-space dataset.

Each processed QM9 molecule receives one deterministic 16-dimensional latent vector. The exported vectors are aligned with molecule identifiers, canonical SMILES, descriptors, and train/validation/test labels.

This artifact is the shared input for the completed PCA, UMAP, property-colored visualization, latent-neighbor analysis, browser-data export, and interactive explorer workflows.

## Reproducible command

Run:

```bash
python -m backend.export_latent_vectors
```

The export configuration is stored in:

`configs/qm9_latent_export.yaml`

## Deterministic latent representation

The VAE encoder produces two outputs:

- latent mean: `mu`;
- latent log variance: `log_var`.

This export saves `mu`, the deterministic encoder mean vector.

The project intentionally does not sample a random latent vector during export.Using the latent mean ensures that the same trained checkpoint and input molecule always produce the same latent coordinates.
## Generated artifacts

- `data/processed/qm9/latent_vectors.npy`
- `data/processed/qm9/latent_metadata.csv`
- `data/processed/qm9/latent_export_manifest.json`

These generated artifacts are excluded from Git.

## Artifact schema

### latent_vectors.npy

A float32 matrix with shape:

`(number_of_molecules, latent_dimensions)`

For the current QM9 baseline:

`(10000, 16)`

Row i corresponds exactly to row i in `latent_metadata.csv`.

### latent_metadata.csv

A CSV file containing:

- latent_row
- source_index
- molecule id
- canonical smiles
- molecular descriptors generated during preprocessing
- QM9 HOMO-LUMO gap when available
- deterministic split label: train, validation, or test

### latent_export_manifest.json

A provenance file recording:

- artifact schema version;
- latent representation type;
- molecule count;
- latent dimensionality;
- export batch size;
- checkpoint path and selected validation epoch;
- input artifact paths;
- output artifact paths;
- split sizes;
- metadata columns.

## Current scientific scope

The exported coordinates enable reproducible latent-space analysis, but they do not alone prove that the representation is chemically meaningful.

The completed downstream analyses include:

- training-fitted PCA and UMAP projections;
- molecular-property-colored latent maps;
- test-to-training nearest-neighbor retrieval;
- Morgan-fingerprint Tanimoto comparison;
- fingerprint reconstruction evaluation;
- browser-ready scientific data export;
- interactive molecular exploration.

The results show enrichment for fingerprint similarity relative to random references, while also showing that Euclidean latent distance is not a complete molecular-similarity measure.