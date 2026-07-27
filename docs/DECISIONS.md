# Design Decisions

This document records significant technical decisions made during development. Each decision describes the current choice, its motivation, its tradeoffs, and the conditions under which it should be reconsidered.

## Decision 001 — Use Morgan fingerprints as the initial molecular representation

**Date:** July 2026

**Context:**  
The project requires a fixed-size numerical representation of molecular structures for the first VAE baseline.

**Choice:**  
Use RDKit Morgan fingerprints with radius 2 and 2048 bits.

**Reason:**  

- Morgan fingerprints are widely used in cheminformatics.
- They provide a fixed-dimensional binary input.
- They work well with a dense neural-network baseline.
- They allow the preprocessing pipeline to be implemented and validated quickly.

**Tradeoff:**  
Morgan fingerprints do not preserve explicit atom and bond graph structure in a directly decodable form.

**Future reconsideration:**  
Evaluate graph-based representations when the project moves to a Graph VAE or molecular graph generator.

## Decision 002 — Use a dense VAE as the initial generative baseline

**Date:** July 2026

**Context:**  
The first model must consume fixed-length 2048-bit fingerprint vectors.

**Choice:**  
Use a fully connected encoder and decoder rather than a convolutional or graph architecture.

**Reason:**  

- The fingerprint input is a one-dimensional fixed-size vector.
- Dense layers provide a simple and appropriate baseline.
- The implementation allows the project to validate VAE training, reconstruction loss, KL divergence, and latent-space behavior before introducing more complex architectures.

**Tradeoff:**  
The model reconstructs fingerprint features rather than molecular graphs or valid SMILES.

**Future reconsideration:**  
Introduce a Graph VAE when the project is ready to model atoms, bonds, and molecular validity directly.

## Decision 003 — Start with a 16-dimensional latent space

**Date:** July 2026

**Context:**  
The model needs a compressed representation that remains expressive while being practical to analyze and project.

**Choice:**  
Use a latent dimension of 16 for the initial Fingerprint VAE configuration.

**Reason:**  

- It creates a substantial reduction from 2048 fingerprint bits.
- It remains large enough to preserve multiple molecular factors.
- It is suitable for later PCA or UMAP visualization.
- It provides a clear baseline for dimensionality experiments.

**Tradeoff:**  
The selected dimension has not yet been compared with alternative latent sizes.

**Future reconsideration:**  
Compare 8, 16, 32, and 64 dimensions after a larger dataset and test protocol are available.

## Decision 004 — Use YAML experiment configuration

**Date:** July 2026

**Context:**  
Training settings were originally hard-coded in the training script.

**Choice:**  
Store dataset paths, model dimensions, training hyperparameters, seed, and checkpoint path in `configs/fingerprint_vae.yaml`.

**Reason:**  

- Improves reproducibility.
- Separates experiment settings from implementation logic.
- Allows later experiments to be compared through version-controlled configuration files.

**Tradeoff:**  
Configuration validation is intentionally lightweight at the current project stage.

**Future reconsideration:**  
Add stronger schema validation and per-experiment configuration files when multiple datasets and model variants are introduced.

## Decision 005 — Add deterministic validation before scaling the dataset

**Date:** July 2026

**Context:**  
The original training workflow used every processed molecule for optimization and had no evaluation-only metric path.

**Choice:**  
Create a deterministic train/validation split using the configured seed and validation fraction.

**Reason:**  

- Separates optimization data from evaluation data.
- Makes training runs more reproducible.
- Establishes the workflow needed before introducing a larger QM9 subset.

**Tradeoff:**  
The current three-molecule development sample creates only a one-molecule validation set, which is not scientifically meaningful.

**Future reconsideration:**  
Replace the development sample with a documented QM9 subset containing meaningful train, validation, and test partitions.