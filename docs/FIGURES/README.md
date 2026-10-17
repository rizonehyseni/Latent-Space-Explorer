# Figures 

This directory contains versioned scientific figures generated from reproducible project artifacts.

## Current figures

| File | Description | Documentation |
|---|---|---|
| `qm9-fingerprint-vae-training-curves-v1.png` | Training and validation total VAE loss, reconstruction loss, and KL divergence for the first QM9 Fingerprint VAE baseline. | [EXPERIMENTS.md](../EXPERIMENTS.md) |
| `qm9-latent-pca-by-split-v1.png` | PCA projection of QM9 latent vectors, colored by train, validation, and test split. | [LATENT_SPACE_ANALYSIS.md](../LATENT_SPACE_ANALYSIS.md) |
| `qm9-latent-umap-by-split-v1.png` | UMAP projection of QM9 latent vectors, colored by train, validation, and test split. | [LATENT_SPACE_ANALYSIS.md](../LATENT_SPACE_ANALYSIS.md) |
| `qm9-latent-pca-by-property-v1.png` | PCA projection colored by molecular weight, LogP, TPSA, ring count, and heavy-atom count. | [LATENT_SPACE_ANALYSIS.md](../LATENT_SPACE_ANALYSIS.md) |
| `qm9-latent-umap-by-property-v1.png` | UMAP projection colored by molecular weight, LogP, TPSA, ring count, and heavy-atom count. | [LATENT_SPACE_ANALYSIS.md](../LATENT_SPACE_ANALYSIS.md) |
| `qm9-latent-distance-vs-tanimoto-v1.png` | Relationship between 16D latent distance and Morgan-fingerprint Tanimoto similarity. | [LATENT_NEIGHBOR_ANALYSIS.md](../LATENT_NEIGHBOR_ANALYSIS.md) |
| `qm9-neighbor-tanimoto-vs-random-v1.png` | Tanimoto distributions for latent nearest neighbors and random training references. | [LATENT_NEIGHBOR_ANALYSIS.md](../LATENT_NEIGHBOR_ANALYSIS.md) |
| `qm9-fingerprint-reconstruction-metrics-v1.png` | Held-out test reconstruction metrics using the validation-selected probability threshold. | [FINGERPRINT_RECONSTRUCTION.md](../FINGERPRINT_RECONSTRUCTION.md) |
| `qm9-fingerprint-reconstruction-tanimoto-v1.png` | Per-molecule original-versus-reconstructed fingerprint Tanimoto distribution. | [FINGERPRINT_RECONSTRUCTION.md](../FINGERPRINT_RECONSTRUCTION.md) |
| `qm9-robustness-comparison-v1.png` | Mean VAE loss, reconstruction F1, and Tanimoto similarity across latent dimensions and random seeds. | [ROBUSTNESS_ANALYSIS.md](../ROBUSTNESS_ANALYSIS.md) |

## Application screenshots

Captured from the deployed web explorer. They show the interface, not new experimental results.

| File | Description | Documentation |
|---|---|---|
| `explorer-umap-overview-v1.png` | Default desktop view: UMAP projection of all 10,000 molecules colored by HOMO–LUMO gap. | [Web application](../../web/README.md) |
| `explorer-pca-ring-count-v1.png` | PCA projection colored by ring count. | [Web application](../../web/README.md) |
| `explorer-molecule-inspector-v1.png` | Molecule inspector for held-out test molecule `gdb_10005`, with properties and its ten nearest training neighbors. | [Web application](../../web/README.md) |
| `explorer-mobile-v1.png` | Phone layout at 390 px width, with the map shown before the controls. | [Web application](../../web/README.md) |
| `explorer-demo-v1.gif` | Short walkthrough: switching projections and color properties, searching a molecule, and opening a neighbor. | [Web application](../../web/README.md) |

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