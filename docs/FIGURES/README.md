# Figures 

This directory contains versioned scientific figures generated from reproducible project artifacts.

## Current figures

| File | Description | Documentation |
|---|---|---|
| `qm9-fingerprint-vae-training-curves-v1.png` | Training and validation total VAE loss, reconstruction loss, and KL divergence for the first QM9 Fingerprint VAE baseline. | [EXPERIMENTS.md](../EXPERIMENTS.md) |
| `qm9-latent-pca-by-split-v1.png` | PCA projection of QM9 latent vectors, colored by train, validation, and test split. | [PCA_ANALYSIS.md](../PCA_ANALYSIS.md) |
| `qm9-latent-umap-by-split-v1.png` | UMAP projection of QM9 latent vectors, colored by train, validation, and test split. | [UMAP_ANALYSIS.md](../UMAP_ANALYSIS.md) |

Every figure added to this directory should:

1. use a descriptive, versioned filename;
2. be generated from saved experiment data or scripts;
3. be explained in the relevant experiment document;
4. include the dataset, model configuration, and metric context;
5. avoid unsupported scientific conclusions.

Example filename format:

```text
qm9-fingerprint-vae-training-curves-v2.png
qm9-latent-space-umap-v1.png
qm9-property-colored-latent-space-v1.png