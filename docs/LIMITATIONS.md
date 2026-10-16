# Current Limitations

This document records the current scientific and engineering limitations of Latent Space Explorer.

## Molecular representation

The current baseline uses Morgan fingerprints as input and output.

This means the model learns a compressed representation of fixed-length molecular fingerprints, not a direct representation of molecular graphs.

Therefore:

- latent-space exploration is possible;
- fingerprint reconstruction is possible;
- direct molecular-graph generation is not implemented;
- latent vectors cannot be decoded into guaranteed valid SMILES strings.

A future Graph VAE, sequence-based VAE, or molecular diffusion model would be required for chemically valid molecular generation.

## Evaluation coverage

The first QM9 baseline includes deterministic train, validation, and held-out test partitions.

The current evaluation includes training losses, latent-neighbor similarity, held-out fingerprint reconstruction metrics, and a nine-run comparison across three seeds and three latent dimensions.

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
- more random seeds, including seed variation in the neighbor and property analyses;
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
- the map requires a browser with WebGL enabled.

## Reproducibility scope

The dataset preparation, split creation, training configuration, and reported results are reproducible from the documented configurations. Seeds are recorded in every configuration, and GitHub Actions runs the backend tests on Python 3.12 for every pull request.

Remaining gaps:

- `matplotlib`, `scikit-learn`, `umap-learn`, and `PyYAML` use minimum versions rather than exact pins;
- the original results were produced on Windows, and the full pipeline has not been rerun end to end on another platform;
- hardware metadata is not recorded;
- experiment reports are written by hand rather than generated automatically.
