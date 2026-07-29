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

However, the current evaluation is limited to total VAE loss, reconstruction loss, and KL divergence.

The project does not yet measure:

- fingerprint bit-level reconstruction accuracy;
- Tanimoto similarity between original and reconstructed fingerprints;
- nearest-neighbor molecular similarity;
- molecular-property preservation;
- latent-cluster quality;
- variance across multiple random seeds.

The current result is therefore a training baseline, not yet evidence of chemically meaningful latent organization.

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

Latent vectors are not yet exported as a documented dataset artifact.

As a result, the project does not yet provide:

- PCA, UMAP, or t-SNE projections;
- latent-space cluster analysis;
- property-colored latent maps;
- nearest-neighbor exploration;
- interpolation trajectories;
- interactive 3D exploration.

Latent export and analysis are the next planned research stage.

## Frontend scope

The frontend is currently a React and Vite foundation.

It does not yet load trained-model artifacts or display molecular data.

The future explorer will require:

- a latent-coordinate data format;
- molecular metadata and descriptor files;
- a 2D or 3D projection pipeline;
- molecule selection and inspection;
- a rendering layer such as Three.js or React Three Fiber.

## Reproducibility scope

The dataset preparation, split creation, training configuration, and baseline result are reproducible.

However, fully repeatable research reporting will later require:

- environment lock files;
- recorded package versions;
- hardware metadata;
- seed logging for every experiment;
- experiment comparison tables;
- automated report generation.