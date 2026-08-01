# Project Status

## Current phase

The project has completed its first reproducible QM9 Fingerprint VAE baseline, deterministic latent-vector export, PCA and UMAP projections, and molecular-property-colored latent-space visualizations.

The current system can prepare a deterministic QM9 subset, generate Morgan fingerprints, create non-overlapping train/validation/test splits, train and evaluate a dense Variational Autoencoder, export deterministic latent vectors, and visualize the latent space by dataset split and molecular properties.


## Completed work

| Area | Completed work |
|---|---|
| Repository foundation | Modular backend, configuration files, documentation structure, and Git workflow established |
| Molecular preprocessing | RDKit validation, canonical SMILES generation, Morgan fingerprint generation |
| Development smoke dataset | Three-molecule sample dataset for ingestion and pipeline checks |
| QM9 dataset preparation | Deterministic 10,000-molecule QM9 subset with provenance manifest |
| Dataset splitting | Deterministic 8,000 / 1,000 / 1,000 train, validation, and test partitions |
| Baseline model | Dense Fingerprint VAE with a 16-dimensional latent space |
| Training evaluation | Best checkpoint selected by validation loss and evaluated once on the held-out test split |
| Result documentation | Baseline metrics and training curves recorded in the experiment documentation |
| Latent export | Deterministic 16-dimensional latent mean vectors exported for all 10,000 QM9 molecules |
| PCA visualization | Training-fitted two-dimensional PCA projection generated and documented |
| UMAP visualization | Training-fitted two-dimensional UMAP projection generated and documented |
| Property visualization | PCA and UMAP projections colored by five aligned molecular properties |

## Current baseline result

The first QM9 Fingerprint VAE baseline was trained for 50 epochs on CPU.

| Metric | Result |
|---|---:|
| Best validation epoch | 50 |
| Best validation loss | 75.1559 |
| Test total VAE loss | 74.8792 |
| Test reconstruction loss | 68.5376 |
| Test KL divergence | 6.3416 |

These values establish a baseline. They do not yet demonstrate that the latent space is chemically meaningful.

## Current evidence


The repository currently includes:

- a reproducible QM9 preparation workflow;
- deterministic and non-overlapping dataset splits;
- a saved best model checkpoint and held-out test metrics;
- deterministic 16-dimensional latent vectors aligned with molecule metadata;
- a PCA projection retaining 42.8% of latent variance in two components;
- a training-fitted nonlinear UMAP projection;
- PCA and UMAP figures colored by dataset split;
- PCA and UMAP figures colored by molecular weight, LogP, TPSA, ring count, and heavy-atom count;
- automated tests for projection fitting, artifact alignment, property alignment, and figure generation.

The property-colored figures show visible variation across parts of the projected latent space. LogP, TPSA, and ring count exhibit local patterns, particularly in the UMAP projection.

These figures provide exploratory evidence that molecular-property information may be represented in the latent vectors. They do not quantify chemical similarity or prove that visible UMAP regions are chemically meaningful clusters.

See [PCA_ANALYSIS.md](PCA_ANALYSIS.md), [UMAP_ANALYSIS.md](UMAP_ANALYSIS.md), and [PROPERTY_ANALYSIS.md](PROPERTY_ANALYSIS.md) for the documented methods, results, interpretations, and limitations.

## Known limitations

The current model reconstructs fixed-length Morgan fingerprints rather than molecular graphs or SMILES strings. Therefore, it cannot directly generate chemically valid molecular structures.

The model has not yet been evaluated with:

- fingerprint bit-level reconstruction accuracy;
- reconstructed-fingerprint Tanimoto similarity;
- latent nearest-neighbor retrieval;
- quantitative latent-distance versus fingerprint-similarity analysis;
- molecular-property prediction;
- repeated runs across multiple seeds;
- alternative latent dimensions;
- alternative model architectures.

Two-dimensional PCA and UMAP visualizations cannot establish that the original 16-dimensional latent space is chemically meaningful.

## Current work

The molecular-property-colored PCA and UMAP analysis is complete.

The visualization workflow validates row-level alignment across latent coordinates, molecule identifiers, canonical SMILES, split labels, and molecular properties. Both projection methods use the same property values and consistent color limits.


## Next planned step

The next branch should evaluate nearest neighbors in the original 16-dimensional latent space and compare latent distance with Morgan-fingerprint Tanimoto similarity.

That branch should:

1. use held-out test molecules as queries;
2. use training molecules as the reference set;
3. identify nearest neighbors using the original 16-dimensional latent vectors rather than PCA or UMAP coordinates;
4. calculate Morgan-fingerprint Tanimoto similarity for retrieved neighbors;
5. compare nearest-neighbor similarity against a deterministic random baseline;
6. export aligned, versioned neighbor and summary artifacts;
7. generate quantitative figures and representative molecule examples;
8. document whether smaller latent distances correspond to higher fingerprint similarity.

After nearest-neighbor analysis, the project should add fingerprint reconstruction-quality metrics and repeated experiments across multiple seeds.