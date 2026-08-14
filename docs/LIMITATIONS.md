# Current Limitations

This document records the current scientific and engineering limitations of the Molecular Latent Space Explorer.

## Molecular representation

The current baseline uses Morgan fingerprints as input and output.

This means the model learns a compressed representation of fixed-length molecular fingerprints, not a direct representation of molecular graphs.

Therefore:

- latent-space exploration is possible;
- fingerprint reconstruction is possible;
- direct molecular-graph generation is not implemented;
- generated latent vectors cannot yet be decoded into guaranteed valid SMILES strings.

A future Graph VAE, sequence-based VAE, or molecular diffusion model would be required for chemically valid molecular generation.

## Evaluation coverage

The first QM9 baseline includes deterministic train, validation, and held-out test partitions.

The current evaluation includes training losses, latent-neighbor similarity, and held-out fingerprint reconstruction metrics.

The project does not yet measure:

- molecular-property preservation after reconstruction;
- statistically validated latent-cluster quality;
- reconstruction of valid molecular graphs or SMILES.

The results provide evidence that the latent representation enriches for fingerprint similarity relative to random references, but they do not establish complete chemical, biological, or functional organization.

## Dataset scope

The current experiment uses a deterministic 10,000-molecule subset of QM9.

This is appropriate for an initial CPU-friendly baseline, but it is not the complete QM9 collection.

Future experiments should compare:

- different subset sizes;
- the full QM9 dataset where practical;
- multiple random seeds;
- additional molecular datasets;
- property-balanced or scaffold-aware splits.

## Latent-space analysis

Deterministic latent vectors are exported as an aligned dataset artifact. The project now includes:

- training-fitted PCA and UMAP projections;
- molecular-property-colored latent maps;
- held-out test-to-training nearest-neighbor retrieval;
- Morgan-fingerprint Tanimoto comparison;
- a deterministic random-similarity baseline.

Latent nearest neighbors have higher mean fingerprint similarity than random training molecules. However, the relationship between Euclidean latent distance and Tanimoto similarity is weak.

## Frontend scope

The React, Vite, and Plotly explorer loads validated static scientific artifacts and supports:

- interactive PCA and UMAP visualization;
- molecular-property coloring;
- molecule search and selection;
- dataset-split and property-range filtering;
- molecular-property inspection;
- latent-neighbor and Tanimoto comparison.

Current frontend limitations include:

- no direct model inference in the browser;
- no molecular-structure drawing;
- no latent interpolation interface;
- no three-dimensional projection;
- neighbor tables are limited to exported held-out test queries;
- deployment and final responsive-layout validation remain incomplete.

## Reproducibility scope

The dataset preparation, split creation, training configuration, and baseline result are reproducible.

However, fully repeatable research reporting will later require:

- environment lock files;
- recorded package versions;
- hardware metadata;
- seed logging for every experiment;
- experiment comparison tables;
- automated report generation.