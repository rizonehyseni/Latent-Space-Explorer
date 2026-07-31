# Project Status

## Current phase

The project has completed its first reproducible QM9 Fingerprint VAE baseline and its first latent-space visualization.

The current system can prepare a deterministic QM9 subset, generate Morgan fingerprints, create non-overlapping train/validation/test splits, train a dense Variational Autoencoder, select the best checkpoint using validation loss, evaluate the held-out test split, export deterministic latent vectors, and generate a PCA latent-space figure.

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

## Current evidence

The repository currently includes:

- a reproducible QM9 preparation workflow;
- deterministic dataset splits;
- unit tests for split determinism and non-overlap;
- a saved best model checkpoint;
- saved test metrics;
- a training-history figure showing total loss, reconstruction loss, and KL divergence;
- deterministic latent vectors aligned with molecular metadata and split labels;
- a PCA latent-space figure with 42.8% total explained variance.

See [EXPERIMENTS.md](EXPERIMENTS.md) and [PCA_ANALYSIS.md](PCA_ANALYSIS.md) for the documented results.

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

The first QM9 latent-space visualization is complete.

PCA was fitted on the 8,000-molecule training split and applied to all 10,000 latent vectors. The first two components explain 42.8% of the variance, while training, validation, and test molecules overlap across the same broad projected regions.

See [PCA_ANALYSIS.md](PCA_ANALYSIS.md) for the method, figure, interpretation, and limitations.

## Next planned step

The next branch should generate a UMAP projection of the same QM9 latent vectors.

That branch should:

1. use the same exported latent vectors and aligned metadata;
2. define and save explicit UMAP parameters;
3. fit the projection using the training split;
4. transform or document the treatment of validation and test molecules;
5. generate a versioned UMAP figure colored by split;
6. compare PCA and UMAP without claiming chemical meaning prematurely.

After UMAP, the project can begin property-colored visualizations and nearest-neighbor similarity analysis.