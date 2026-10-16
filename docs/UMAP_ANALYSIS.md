# QM9 Latent UMAP Analysis

## Purpose

This document records the first nonlinear two-dimensional visualization of the QM9 Fingerprint VAE latent space.

The analysis projects deterministic 16-dimensional latent mean vectors into two dimensions using Uniform Manifold Approximation and Projection (UMAP).

## Reproducible Command

Run:

```bash
python -m backend.plot_latent_umap --config configs/qm9_latent_umap.yaml
```

Configuration:

```text
configs/qm9_latent_umap.yaml
```

## Method

The workflow uses:

- deterministic latent mean vectors for 10,000 QM9 molecules;
- a two-dimensional UMAP projection;
- fitting on the 8,000-molecule training split only;
- transformation of the 1,000 validation and 1,000 test molecules using the training-fitted UMAP model;
- explicit random seeds for fitting and transformation;
- Euclidean distance in the 16-dimensional latent space.

Fitting UMAP only on training vectors prevents validation and test molecules from influencing the learned projection.

## Configuration

| Parameter | Value |
|---|---|
| Input latent dimensions | 16 |
| Output dimensions | 2 |
| Fitting split | Training |
| Training molecules | 8,000 |
| Validation molecules | 1,000 |
| Test molecules | 1,000 |
| Neighbors | 15 |
| Minimum distance | 0.1 |
| Metric | Euclidean |
| Random state | 42 |
| Transform seed | 42 |

## Figure

![QM9 Fingerprint VAE latent UMAP projection](FIGURES/qm9-latent-umap-by-split-v1.png)

**Figure 3.** *UMAP projection of deterministic 16-dimensional QM9 Fingerprint VAE latent mean vectors. UMAP was fitted on the training split and then used to transform validation and test molecules. All three splits occupy the same projected regions.*

## Interpretation

The UMAP projection contains several separated regions and locally connected structures. Training, validation, and test points remain intermingled throughout these regions rather than forming split-specific groups. This is consistent with the three deterministic dataset partitions having similar overall latent distributions.

This split-colored figure alone cannot establish chemically meaningful clusters. The completed property-colored maps show systematic descriptor variation across several projected regions, and the latent-neighbor evaluation shows greater fingerprint similarity than the random baseline. These results support non-random molecular organization, while the weak distance-similarity correlation prevents interpreting UMAP proximity as complete chemical similarity.

## Comparison with PCA

PCA provides a linear global overview in which the first two components explain 42.8% of the latent variance. UMAP produces a more visibly separated nonlinear layout and emphasizes local neighborhood relationships.

The shapes, distances, orientation, and sizes of UMAP regions should not be compared directly with PCA geometry. UMAP does not provide an explained-variance measure, and large distances between projected regions do not necessarily represent proportional distances in the original latent space.

Together, PCA and UMAP show that the dataset splits cover similar projected regions. Their interpretation is strengthened by the separate property and neighbor analyses, but neither two-dimensional visualization should be treated as a complete molecular-similarity metric.

## Limitations

## Limitations

- UMAP can distort global distances, region sizes, orientation, and relative positions.
- The projection depends on its selected parameters and random seeds.
- Two-dimensional proximity does not preserve every relationship from the 16-dimensional latent space.
- The split-colored figure does not directly display molecular-property values.
- Tanimoto enrichment is measured in the original latent-neighbor experiment, not from visual UMAP distance.
- The visualization does not directly measure fingerprint reconstruction quality.

Related evidence is documented in [PROPERTY_ANALYSIS.md](PROPERTY_ANALYSIS.md), [LATENT_NEIGHBOR_ANALYSIS.md](LATENT_NEIGHBOR_ANALYSIS.md), and [FINGERPRINT_RECONSTRUCTION.md](FINGERPRINT_RECONSTRUCTION.md).

