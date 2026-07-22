# Project Status

## Current point in the project

The project is in **Phase I: Fingerprint VAE baseline**. The data-to-model path is implemented and the training experiment is now configured through YAML. The project is not yet at the visualization or molecular-generation stage.

The current system can process SMILES data, create Morgan fingerprints, train a dense VAE, and save a checkpoint with its experiment metadata. Its current sample dataset is deliberately small and exists to confirm that the pipeline works end to end.

## Completed work

| Area | Completed capability |
| --- | --- |
| Data ingestion | Reads a CSV containing a required `smiles` column and reports missing files or columns. |
| Molecular preprocessing | Validates SMILES with RDKit, canonicalizes valid molecules, and skips invalid entries. |
| Molecular metadata | Calculates molecular weight, LogP, atom counts, hydrogen-bond counts, TPSA, and ring count. |
| Model input | Produces fixed-length 2048-bit Morgan fingerprints and stores them as a NumPy matrix. |
| VAE model | Implements a dense encoder/decoder, 16-dimensional latent representation, reparameterization, and fingerprint reconstruction logits. |
| Training | Uses binary cross-entropy with logits plus KL divergence, Adam optimization, CPU/CUDA selection, epoch metrics, and checkpoint saving. |
| Reproducibility | Uses `configs/fingerprint_vae.yaml` for the seed, paths, model dimensions, training settings, and checkpoint destination. |
| Documentation | Documents the current architecture and separates implemented features from planned work. |

## What is not complete yet

- The tracked dataset has only a few molecules; it is not large enough for meaningful scientific evaluation.
- Training currently uses all processed molecules, with no validation or test split.
- There are no reconstruction-quality, validity, or property-prediction evaluation metrics beyond the training loss.
- Latent vectors are not exported for use by the browser.
- The React/Vite frontend is still a starter scaffold; it has no Three.js scene, molecular data loader, or model integration.
- The model operates on fingerprints. It does not decode into valid SMILES or molecular graphs.

## Planned sequence

1. **Training evaluation:** add a deterministic train/validation split and report validation reconstruction, KL, and total losses.
2. **Larger dataset:** replace the development sample with a documented QM9 subset and retain a held-out test set.
3. **Latent export:** encode processed molecules with their mean latent vector and write metadata plus display coordinates to a versioned JSON artifact.
4. **Explorer MVP:** replace the frontend starter screen with a point-cloud view of exported molecules, then add selection and descriptor filtering.
5. **Interpolation:** support selecting two molecules and inspect a latent-space trajectory before claiming decoded molecular validity.
6. **Advanced representation:** evaluate a graph VAE or another structured molecular representation. A convolutional VAE should be considered only after defining an input representation where convolution is meaningful.

## Definition of success for the current phase

Phase I is complete when the project can train and evaluate the Fingerprint VAE on a meaningful held-out dataset, record the experiment configuration and metrics, and export stable latent representations for visualization. The model does not need to generate chemically valid molecules to complete this phase.
