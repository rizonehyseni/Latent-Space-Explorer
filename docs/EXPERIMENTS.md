# Experiment Records

This document records completed runs that provide evidence about the model. Results from development samples are retained to verify the pipeline, but are not treated as scientific conclusions.

## Fingerprint VAE validation pipeline check

**Date:** 2026-07-27  
**Purpose:** Verify that the configurable deterministic train/validation workflow executes end to end.  
**Dataset:** `data/qm9_sample.csv` with 3 molecules.  
**Configuration:** `configs/fingerprint_vae.yaml`  
**Seed:** 42  
**Split:** 2 training molecules, 1 validation molecule  
**Model:** Dense Fingerprint VAE, 2048-bit Morgan fingerprint input, 16-dimensional latent space  
**Training:** 50 epochs, Adam, learning rate 0.001, batch size 64

### Recorded outcome

The preprocessing and training commands completed successfully. Training emitted both training and validation total loss, reconstruction loss, and KL-divergence metrics for all 50 epochs. The model checkpoint was written to `models/molecular_vae.pt`.

| Metric | Value |
| --- | --- |
| Lowest recorded validation loss | 45.9923 at epoch 36 |
| Final training loss | 11.1963 at epoch 50 |
| Final validation loss | 63.6155 at epoch 50 |

### Interpretation

The run verifies that the deterministic split and evaluation-only validation path function correctly. Training loss decreases substantially, demonstrating that the pipeline can fit the small development sample.

The validation result is not scientifically meaningful because it represents a single molecule. Its fluctuations are expected and must not be used to compare model quality or select hyperparameters. A larger documented QM9 subset with a held-out test set is required for meaningful evaluation.

### Evidence to retain

- terminal output showing the dataset split and final checkpoint location;
- the exact YAML configuration used for the run;
- the commit containing the validation implementation;
- training-curve figures once metric export is implemented.
