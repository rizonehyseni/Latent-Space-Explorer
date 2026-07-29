# Project Status

## Current phase

The project has completed its first reproducible QM9 Fingerprint VAE baseline.

The current system can prepare a deterministic QM9 subset, generate Morgan fingerprints, create non-overlapping train/validation/test splits, train a dense Variational Autoencoder, select the best checkpoint using validation loss, evaluate the held-out test split, and generate a training-history figure.

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
- deterministic dataset splits;
- unit tests for split determinism and non-overlap;
- a saved best model checkpoint;
- saved test metrics;
- a training-history figure showing total loss, reconstruction loss, and KL divergence.

See [EXPERIMENTS.md](EXPERIMENTS.md) for the documented baseline result.

## Known limitations

The current model reconstructs fixed-length Morgan fingerprints rather than molecular graphs or SMILES strings. Therefore, it cannot directly generate chemically valid molecular structures.

The model has not yet been evaluated with:

- fingerprint bit-level reconstruction accuracy;
- Tanimoto similarity;
- nearest-neighbor retrieval;
- molecular-property prediction;
- latent-space visualization;
- repeated runs across multiple seeds;
- comparisons against alternative model architectures.

## Next planned step

The next implementation branch should export latent vectors for the QM9 dataset.

That branch should:

1. load the selected QM9 Fingerprint VAE checkpoint;
2. encode molecules into latent vectors;
3. save molecule identifiers, SMILES, descriptors, split labels, and latent coordinates;
4. create a reproducible latent-space artifact for later PCA or UMAP visualization;
5. document the export schema and capture the first latent-space figure.

This is the transition from model training toward latent-space analysis and the future interactive explorer.