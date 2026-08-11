# Project Status

The project has completed its reproducible QM9 Fingerprint VAE pipeline, latent-space analyses, reconstruction and neighbor evaluations, robustness experiments, browser-data export, and interactive web explorer.

The system can prepare QM9 data, train and evaluate the model, export deterministic latent vectors, analyze latent organization, retrieve similar molecules, and interactively explore PCA and UMAP projections in the browser.


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
| Robustness evaluation | Nine runs across three seeds and three latent dimensions |
| Browser data export | Aligned molecule, neighbor, metrics, and manifest JSON generated for the frontend |
| Interactive web explorer | PCA/UMAP visualization, property coloring, molecule search, filtering, property inspection, and neighbor comparison |

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

## Robustness result

Nine models compared latent dimensions `8`, `16`, and `32` across seeds `7`, `42`, and `123`.

| Latent dimensions | Test loss | Reconstruction F1 | Mean Tanimoto |
|---:|---:|---:|---:|
| 8 | 74.9092 ± 0.6494 | 0.4949 ± 0.0118 | 0.3322 ± 0.0110 |
| 16 | 74.7608 ± 0.1595 | 0.4953 ± 0.0034 | 0.3320 ± 0.0034 |
| 32 | 74.6645 ± 0.6494 | 0.4949 ± 0.0098 | 0.3317 ± 0.0090 |

Reconstruction performance remained stable across the tested dimensions. The 16-dimensional configuration showed the lowest variation across seeds.

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
- validation-selected fingerprint reconstruction evaluation;
- nine-run seed and latent-dimension robustness comparison;
- mean and sample-standard-deviation robustness metrics.
- browser-ready data for all 10,000 aligned molecules;
- ten training neighbors for each held-out test query;
- compact scientific metrics and threshold-sweep data;
- SHA-256 integrity checks for browser artifacts.

See [PCA_ANALYSIS.md](PCA_ANALYSIS.md), [UMAP_ANALYSIS.md](UMAP_ANALYSIS.md), [PROPERTY_ANALYSIS.md](PROPERTY_ANALYSIS.md), and [LATENT_NEIGHBOR_ANALYSIS.md](LATENT_NEIGHBOR_ANALYSIS.md).

## Known limitations

The model reconstructs fixed-length Morgan fingerprints rather than molecular graphs or SMILES strings. It therefore cannot directly generate guaranteed-valid molecular structures.

The present study uses a deterministic 10,000-molecule subset of QM9 rather than the complete dataset.

PCA and UMAP are two-dimensional projections and cannot preserve every relationship in the original latent space.

Nearest-neighbor results are available for the 1,000 held-out test queries evaluated against the 8,000 training references.

Tanimoto similarity measures Morgan-fingerprint overlap and should not be interpreted as complete chemical, biological, or functional similarity.

The dense fingerprint VAE is a controlled baseline rather than a state-of-the-art graph-generative architecture.
