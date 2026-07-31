# QM9 Latent PCA Analysis

## Purpose

This document records the first two-dimensional visualization of the QM9 Fingerprint VAE latent space.

The analysis projects deterministic 16-dimensional latent mean vectors into two dimensions using Principal Component Analysis (PCA).

## Reproducible command

Run:

```powershell
python -m backend.plot_latent_pca
```

Configuration:

```text
configs/qm9_latent_pca.yaml
```

## Method

The workflow uses:

- latent vectors exported from the selected QM9 Fingerprint VAE checkpoint;
- one deterministic latent mean vector, μ, for each of 10,000 molecules;
- PCA with two output components;
- PCA fitting on the 8,000-molecule training split only;
- transformation of validation and test molecules using the training-fitted PCA model.

Fitting PCA only on training vectors prevents the validation and test partitions from influencing the learned projection axes.

## Result

| Metric | Value |
| --- | --- |
| Projected molecules | 10,000 |
| Input latent dimensions | 16 |
| PCA output dimensions | 2 |
| PCA fitting split | Training |
| PC1 explained variance | 22.7% |
| PC2 explained variance | 20.1% |
| Total explained variance | 42.8% |

## Figure

![QM9 Fingerprint VAE latent PCA projection](FIGURES/qm9-latent-pca-by-split-v1.png)

*Figure 2. PCA projection of deterministic 16-dimensional QM9 Fingerprint VAE latent mean vectors. PCA was fitted on the 8,000-molecule training split and then applied to validation and test molecules. The three deterministic splits overlap across the same broad regions, indicating that they are distributed similarly in the projected latent space.*

## Interpretation

The first two principal components retain 42.8% of the variance present in the 16-dimensional latent vectors. This makes PCA a useful first overview, but more than half of the variation remains outside the two-dimensional projection.

Training, validation, and test molecules overlap rather than forming visibly separate regions. This is expected for a deterministic random split and provides visual evidence that the partitions have similar overall latent distributions.

The visible density patterns are not yet sufficient evidence of chemically meaningful clusters. The current figure is colored by split membership, not by molecular similarity or molecular properties.

## Limitations

- PCA is a linear projection and may not preserve nonlinear local relationships.
- The projection does not measure fingerprint reconstruction quality.
- The projection does not measure Tanimoto similarity between nearby molecules.
- The figure is not colored by molecular weight, LogP, HOMO-LUMO gap, or another chemical descriptor.
- Visible regions should not be described as chemical clusters without further analysis.
