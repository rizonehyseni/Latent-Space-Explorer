# Project Status

## Current phase

The project has completed its first reproducible QM9 Fingerprint VAE baseline, deterministic latent-vector export, and initial PCA and UMAP latent-space visualizations.

The system can prepare a deterministic QM9 subset, generate Morgan fingerprints, create non-overlapping train/validation/test splits, train a dense Variational Autoencoder, select the best checkpoint using validation loss, evaluate the held-out test split, export deterministic latent vectors, and generate training-fitted PCA and UMAP projections.

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
| UMAP visualization | Training-fitted two-dimensional UMAP projection generated and documented |

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
- a UMAP projection fitted on training vectors;
- tests covering artifact alignment and train-only projection fitting.

PCA retains 42.8% of the latent variance in its first two components. UMAP produces several nonlinear projected regions. In both figures, training, validation, and test molecules occupy the same broad regions.

See [PCA_ANALYSIS.md](PCA_ANALYSIS.md) and [UMAP_ANALYSIS.md](UMAP_ANALYSIS.md) for interpretation and limitations.

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

PCA and UMAP alone cannot establish that the learned latent space is chemically meaningful.

## Current work

The initial split-colored PCA and UMAP visualizations are complete.

Both projections were fitted using only the 8,000-molecule training split and then applied to the validation and test molecules. The dataset splits overlap throughout both projections, providing no evidence of split-specific latent distributions.

## Next planned step

1. select well-defined molecular properties available from QM9 metadata or reproducibly calculate them;
2. validate property alignment with latent-vector rows;
3. produce versioned PCA and UMAP figures using consistent color scales;
4. document visible gradients, regions, and outliers conservatively;
5. avoid treating projected patterns as proof of chemical similarity;
6. add automated tests for property alignment and artifact generation.

After property visualization, the project should compare latent-space nearest neighbors with Morgan-fingerprint Tanimoto similarity.