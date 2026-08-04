# Project Status

## Current phase

The project has completed its first reproducible QM9 Fingerprint VAE baseline, latent-space analyses, latent-neighbor evaluation, and held-out fingerprint reconstruction evaluation.

The current system can prepare QM9 data, train and evaluate a Fingerprint VAE, export deterministic latent vectors, analyze latent organization, retrieve similar molecules, and quantitatively evaluate reconstructed fingerprints.


## Completed work

| Area | Completed work |
|---|---|
| Repository foundation | Modular backend, configuration files, documentation structure, and Git workflow established |
| Molecular preprocessing | RDKit validation, canonical SMILES generation, and Morgan fingerprint generation |
| QM9 dataset preparation | Deterministic 10,000-molecule QM9 subset with provenance manifest |
| Dataset splitting | Deterministic 8,000 / 1,000 / 1,000 train, validation, and test partitions |
| Baseline model | Dense Fingerprint VAE with a 16-dimensional latent space |
| Training evaluation | Best checkpoint selected by validation loss and evaluated once on the held-out test split |
| Latent export | Deterministic latent mean vectors exported for all 10,000 molecules |
| PCA visualization | Training-fitted two-dimensional PCA projection generated and documented |
| UMAP visualization | Training-fitted two-dimensional UMAP projection generated and documented |
| Property visualization | PCA and UMAP projections colored by five aligned molecular properties |
| Neighbor evaluation | Test-to-training latent neighbors evaluated using Morgan-fingerprint Tanimoto similarity |
| Reconstruction evaluation | Validation-selected threshold and held-out test reconstruction metrics |

## Current baseline result

The first QM9 Fingerprint VAE baseline was trained for 50 epochs on CPU.

| Metric | Result |
|---|---:|
| Best validation epoch | 50 |
| Best validation loss | 75.1559 |
| Test total VAE loss | 74.8792 |
| Test reconstruction loss | 68.5376 |
| Test KL divergence | 6.3416 |

## Latent-neighbor result

The analysis uses 1,000 held-out test molecules as queries and 8,000 training molecules as references.

| Metric | Result |
|---|---:|
| Neighbors per query | 10 |
| Mean nearest-neighbor Tanimoto | 0.2312 |
| Mean random-baseline Tanimoto | 0.0774 |
| Absolute mean improvement | 0.1537 |
| Nearest neighbor beats paired random | 94.94% |
| Pearson distance/similarity correlation | -0.1198 |
| Spearman distance/similarity correlation | -0.1252 |

Latent nearest neighbors are approximately three times more similar than random training molecules according to Morgan-fingerprint Tanimoto similarity.

The weak negative distance/similarity correlations show that the latent space enriches for fingerprint similarity, but Euclidean latent distance is not a strong or complete molecular-similarity measure.

## Fingerprint reconstruction result

The reconstruction threshold was selected exclusively on the validation split and then applied once to 1,000 held-out test molecules.

| Metric | Result |
|---|---:|
| Selected probability threshold | 0.25 |
| Bit accuracy | 0.9915 |
| Precision | 0.6106 |
| Recall | 0.4147 |
| F1 score | 0.4940 |
| Mean Tanimoto | 0.3307 |
| All-zero baseline accuracy | 0.9900 |

The high bit accuracy is strongly affected by fingerprint sparsity. F1 and Tanimoto similarity provide more meaningful evidence of reconstruction quality.

## Current evidence

The repository currently includes:

- reproducible QM9 subset preparation and fingerprint generation;
- deterministic non-overlapping dataset splits;
- a saved best model checkpoint and held-out test metrics;
- deterministic 16-dimensional latent vectors;
- training-fitted PCA and UMAP projections;
- split-colored and molecular-property-colored figures;
- test-to-training latent nearest-neighbor retrieval;
- a deterministic random-similarity baseline;
- quantitative latent-distance and Tanimoto analysis;
- automated tests for artifact and row alignment.

See [PCA_ANALYSIS.md](PCA_ANALYSIS.md), [UMAP_ANALYSIS.md](UMAP_ANALYSIS.md), [PROPERTY_ANALYSIS.md](PROPERTY_ANALYSIS.md), and [LATENT_NEIGHBOR_ANALYSIS.md](LATENT_NEIGHBOR_ANALYSIS.md).

## Known limitations

The current model reconstructs fixed-length Morgan fingerprints rather than molecular graphs or SMILES strings. It therefore cannot directly generate chemically valid molecular structures.

The project has not yet evaluated:

- repeated training across multiple random seeds;
- alternative latent dimensions;
- alternative latent-distance metrics;
- alternative model architectures;
- statistical confidence intervals for neighbor evaluation.

Tanimoto similarity measures fingerprint overlap and should not be interpreted as complete chemical, biological, or functional similarity.

## Current work

The held-out fingerprint reconstruction evaluation is complete.

The workflow selects its probability threshold using validation mean Tanimoto similarity, evaluates the selected threshold on the test split, compares it with the standard `0.5` threshold and an all-zero baseline, and exports reproducible metrics and figures.

See [FINGERPRINT_RECONSTRUCTION.md](FINGERPRINT_RECONSTRUCTION.md) for the complete analysis.

## Next planned step

The next scientific phase should evaluate robustness across multiple random seeds and alternative latent dimensions.

This will determine whether the current findings are stable and whether the 16-dimensional latent representation provides a good trade-off between compression and reconstruction quality.