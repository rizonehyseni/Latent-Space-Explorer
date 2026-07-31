# QM9 Latent Vector Export

## Purpose

This artifact converts the selected QM9 Fingerprint VAE checkpoint into a reusable latent-space dataset.

Each processed QM9 molecule receives one deterministic 16-dimensional latent vector. The exported vectors are aligned with molecule identifiers, canonical SMILES, descriptors, and train/validation/test labels.

This artifact is the input for future PCA, UMAP, nearest-neighbor analysis, property-colored latent maps, and the interactive explorer.

## Reproducible command

Run:

```powershell
python -m backend.export_latent_vectors