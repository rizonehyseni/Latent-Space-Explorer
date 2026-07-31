# QM9 Latent Vector Export

## Purpose

This artifact converts the selected QM9 Fingerprint VAE checkpoint into a reusable latent-space dataset.

Each processed QM9 molecule receives one deterministic 16-dimensional latent vector. The exported vectors are aligned with molecule identifiers, canonical SMILES, descriptors, and train/validation/test labels.

This artifact is the input for future PCA, UMAP, nearest-neighbor analysis, property-colored latent maps, and the interactive explorer.

## Reproducible command

Run:

```powershell
python -m backend.export_latent_vectors
```

The export configuration is stored in:

`configs/qm9_latent_export.yaml`

## Deterministic latent representation

The VAE encoder produces two outputs:

- latent mean: μ
- latent log variance: log σ²

This export saves μ, the encoder mean vector.

The project intentionally does not sample a random latent vector during export. Using μ ensures that the same trained checkpoint and the same input molecule always produce the same latent coordinates.

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

The exported coordinates make latent-space analysis possible, but they do not alone prove that the representation is chemically meaningful.

The next step is to project the 16-dimensional vectors with PCA and UMAP, then test whether nearby points share fingerprint similarity or molecular-property patterns.