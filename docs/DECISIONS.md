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
Latent dimensionality changes compression capacity but did not materially change reconstruction performance across the tested 8-, 16-, and 32-dimensional configurations.

**Outcome:**  
Nine robustness runs across three seeds showed similar reconstruction performance for 8, 16, and 32 dimensions. The 16-dimensional configuration showed the lowest variation and remains the primary baseline.

**Future reconsideration:**  
Reassess the latent dimension when using the complete QM9 dataset, alternative molecular representations, or graph-based architectures.

## Decision 004 - Use separate YAML configuration profiles

**Date:** July 2026

**Choice:**  
Use separate YAML configuration profiles for development, dataset preparation, preprocessing, and QM9 baseline training.

Current configuration files:

```text
configs/fingerprint_vae.yaml
configs/qm9_subset.yaml
configs/qm9_processing.yaml
configs/qm9_fingerprint_vae.yaml
```
**Reason:**  
Different project stages require different parameters. Keeping configurations separate makes experiments easier to reproduce and prevents development settings from being confused with QM9 baseline settings.

**Tradeoff:**  
More configuration files require clearer documentation and validation.

**Outcome:**
The current QM9 baseline can be reproduced from explicit dataset and training configurations.

## Decision 005 - Use a deterministic 10,000-molecule QM9 subset

**Date:** July 2026

**Choice:**  
Use a deterministic 10,000-molecule QM9 subset with 8,000 training, 1,000 validation, and 1,000 test molecules for the first baseline.

**Reason:**  

The subset is large enough to move beyond a smoke test while remaining practical for CPU-based development and reproducible experimentation.

**Tradeoff:**  
The subset does not represent the full QM9 collection and may not capture all molecular diversity.

**Outcome:**
The first baseline now uses validation loss for checkpoint selection and evaluates the selected checkpoint once on a held-out test split.

## Decision 006

Date:  
July 2026

**Choice:** 
Select the QM9 Fingerprint VAE checkpoint using validation loss and reserve the test split for final evaluation.

**Reason:**
Using the test split during model selection would bias the reported test result. Validation performance provides a separate signal for checkpoint selection.

**Tradeoff:**  
The project must maintain deterministic and non-overlapping split indices.

**Outcome:**
The baseline selected epoch 50 as the best validation checkpoint and reported held-out test metrics only after selection.