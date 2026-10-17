# QM9 Latent-Space Analysis

## Purpose

This document records the two-dimensional visualizations of the QM9 Fingerprint VAE latent space and what they show.

Deterministic 16-dimensional latent mean vectors are projected into two dimensions with Principal Component Analysis (PCA) and Uniform Manifold Approximation and Projection (UMAP). The same projections are then colored by dataset split and by molecular properties.

## Reproducible commands

Run:

```bash
python -m backend.plot_latent_pca --config configs/qm9_latent_pca.yaml
python -m backend.plot_latent_umap --config configs/qm9_latent_umap.yaml
python -m backend.plot_latent_properties --config configs/qm9_property_visualizations.yaml
```

The property figures reuse the PCA and UMAP coordinates, so run the projection commands first.

## Method

Both projections use:

- latent vectors exported from the selected QM9 Fingerprint VAE checkpoint;
- one deterministic latent mean vector for each of 10,000 molecules;
- two output dimensions;
- fitting on the 8,000-molecule training split only;
- transformation of the 1,000 validation and 1,000 test molecules using the training-fitted model.

Fitting only on training vectors prevents the validation and test partitions from influencing the learned projection.

UMAP uses the following configuration:

| Parameter | Value |
|---|---|
| Neighbors | 15 |
| Minimum distance | 0.1 |
| Metric | Euclidean |
| Random state | 42 |
| Transform seed | 42 |

## PCA projection

| Metric | Value |
| --- | --- |
| Projected molecules | 10,000 |
| Input latent dimensions | 16 |
| PCA output dimensions | 2 |
| PCA fitting split | Training |
| PC1 explained variance | 22.7% |
| PC2 explained variance | 20.1% |
| Total explained variance | 42.8% |

![QM9 Fingerprint VAE latent PCA projection](FIGURES/qm9-latent-pca-by-split-v1.png)

*Figure 2. PCA projection of deterministic 16-dimensional QM9 Fingerprint VAE latent mean vectors. PCA was fitted on the 8,000-molecule training split and then applied to validation and test molecules. The three deterministic splits overlap across the same broad regions, indicating that they are distributed similarly in the projected latent space.*

The first two principal components retain 42.8% of the variance present in the 16-dimensional latent vectors. This makes PCA a useful first overview, but more than half of the variation remains outside the two-dimensional projection.

Training, validation, and test molecules overlap rather than forming visibly separate regions. This is expected for a deterministic random split and provides visual evidence that the partitions have similar overall latent distributions.

## UMAP projection

![QM9 Fingerprint VAE latent UMAP projection](FIGURES/qm9-latent-umap-by-split-v1.png)

*Figure 3. UMAP projection of deterministic 16-dimensional QM9 Fingerprint VAE latent mean vectors. UMAP was fitted on the training split and then used to transform validation and test molecules. All three splits occupy the same projected regions.*

The UMAP projection contains several separated regions and locally connected structures. Training, validation, and test points remain intermingled throughout these regions rather than forming split-specific groups. This is consistent with the three deterministic dataset partitions having similar overall latent distributions.

## Comparison of PCA and UMAP

PCA provides a linear global overview in which the first two components explain 42.8% of the latent variance. UMAP produces a more visibly separated nonlinear layout and emphasizes local neighborhood relationships.

The shapes, distances, orientation, and sizes of UMAP regions should not be compared directly with PCA geometry. UMAP does not provide an explained-variance measure, and large distances between projected regions do not necessarily represent proportional distances in the original latent space.

The split-colored figures alone cannot establish chemically meaningful clusters. They show that the dataset splits cover similar projected regions; the property maps below and the separate neighbor analysis test whether the organization is chemically meaningful.

## Molecular-property maps

The property figures keep the PCA and UMAP coordinates unchanged. Each molecule remains at the same projected position in every panel, while its color changes according to the selected molecular property.

PCA metadata, UMAP metadata, molecule identifiers, canonical SMILES, split labels, and molecular-property values are validated for row-level alignment before either figure is generated.

| Property | Minimum | Maximum | Mean | Median |
|---|---:|---:|---:|---:|
| Molecular weight (Da) | 16.043 | 144.092 | 122.751 | 125.127 |
| LogP | -2.6147 | 3.4687 | 0.3266 | 0.2864 |
| TPSA | 0.00 | 122.78 | 36.71 | 35.53 |
| Ring count | 0 | 8 | 1.7504 | 1 |
| Heavy-atom count | 1 | 9 | 8.7978 | 9 |

Colors are clipped at the first and ninety-ninth percentiles to reduce visual domination by extreme values. The underlying property values are not modified.

![QM9 PCA projection colored by molecular properties](FIGURES/qm9-latent-pca-by-property-v1.png)

*Figure 4. PCA projection of deterministic 16-dimensional latent mean vectors colored by molecular weight, LogP, TPSA, ring count, and heavy-atom count. Every panel uses the same PCA coordinates.*

The PCA panels show broad overlapping property distributions rather than sharply separated groups. TPSA and ring count display visible directional variation across parts of the projection. LogP also varies across the space, but its pattern is not represented by a single simple linear gradient.

Molecular weight and heavy-atom count appear visually similar because these properties are strongly related in this QM9 subset. Most molecules contain close to nine heavy atoms, so the heavy-atom panel has a limited effective color range.

![QM9 UMAP projection colored by molecular properties](FIGURES/qm9-latent-umap-by-property-v1.png)

*Figure 5. Training-fitted UMAP projection of deterministic 16-dimensional latent mean vectors colored by molecular weight, LogP, TPSA, ring count, and heavy-atom count. Every panel uses the same UMAP coordinates.*

UMAP reveals locally connected regions with different property distributions. LogP, TPSA, and ring count show visible local changes across several projected regions. Some UMAP regions contain predominantly lower or higher values, suggesting that local latent neighborhoods may retain molecular-property information.

Molecular weight and heavy-atom count again show related color patterns. Heavy-atom count is visually dominated by molecules with nine heavy atoms because this value is highly frequent in the selected subset.

Both projections suggest that molecular properties are not distributed completely randomly across the latent space. UMAP makes local property patterns more visible, whereas PCA provides a more conservative global overview. The figures provide exploratory evidence of structured property variation, but they do not quantify it.

## Limitations

- PCA is a linear projection and may not preserve nonlinear local relationships; its first two components retain only 42.8% of the latent variance.
- UMAP can distort global distances, region sizes, orientation, and relative positions, and depends on its selected parameters and random seeds.
- Two-dimensional proximity is not identical to distance in the original 16-dimensional space.
- The figures do not measure statistical significance.
- Quantile clipping compresses extreme property values in the color scale.
- Ring count and heavy-atom count are discrete properties displayed with continuous color maps.
- Property gradients do not prove that latent neighbors are chemically similar.
- Visible regions should not be described as chemical clusters without quantitative validation.

## Related analyses

Whether latent proximity corresponds to fingerprint similarity is tested quantitatively in the original 16-dimensional space, not from projected plot distance. See [LATENT_NEIGHBOR_ANALYSIS.md](LATENT_NEIGHBOR_ANALYSIS.md). Reconstruction quality is evaluated separately in [FINGERPRINT_RECONSTRUCTION.md](FINGERPRINT_RECONSTRUCTION.md).
