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

## Current work

The QM9 latent-vector export workflow is implemented.

It exports deterministic 16-dimensional encoder mean vectors for all 10,000 processed QM9 molecules. Each vector is aligned with molecule metadata, descriptors, canonical SMILES, and the deterministic train, validation, or test label.

See [LATENT_EXPORT.md](LATENT_EXPORT.md) for the artifact schema and reproducible command.

## Next planned step

The next branch should create the first scientific latent-space visualizations.

That branch should:

1. load `latent_vectors.npy` and `latent_metadata.csv`;
2. create a PCA projection as a simple interpretable baseline;
3. create a UMAP projection for local-structure exploration;
4. color points by a molecular property such as molecular weight, LogP, or HOMO-LUMO gap;
5. save versioned figures under `docs/FIGURES/`;
6. document careful interpretations and limitations in `EXPERIMENTS.md`.

The first PCA or UMAP figure is the next screenshot milestone for the project.