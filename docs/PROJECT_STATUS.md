# Project Status

## Current phase

The project has completed its first reproducible QM9 Fingerprint VAE baseline, deterministic latent-vector export, PCA and UMAP visualizations, molecular-property analysis, and quantitative latent-neighbor evaluation.

The current system can prepare and split QM9 data, train and evaluate a Fingerprint VAE, export deterministic latent vectors, visualize latent organization, retrieve held-out test neighbors, and compare latent proximity with Morgan-fingerprint Tanimoto similarity.

## Completed work

| Area | Completed work |
|---|---|
| Repository foundation | Modular backend, configuration files, documentation structure, and Git workflow established |
| Molecular preprocessing | RDKit validation, canonical SMILES generation, and Morgan fingerprint generation |
| QM9 dataset preparation | Deterministic 10,000-molecule QM9 subset with provenance manifest |
| Dataset splitting | Deterministic 8,000 / 1,000 / 1,000 train, validation, and test partitions |
| Baseline model | Dense Fingerprint VAE with a 16-dimensional latent space |
| Training evaluation | Best checkpoint selected by validation loss and evaluated once on the held-out test split |
| Latent export | Deterministic latent mean vectors exported for all 10,000 molecules |
| PCA visualization | Training-fitted two-dimensional PCA projection generated and documented |
| UMAP visualization | Training-fitted two-dimensional UMAP projection generated and documented |
| Property visualization | PCA and UMAP projections colored by five aligned molecular properties |
| Neighbor evaluation | Test-to-training latent neighbors evaluated using Morgan-fingerprint Tanimoto similarity |

## Current baseline result

The first QM9 Fingerprint VAE baseline was trained for 50 epochs on CPU.

| Metric | Result |
|---|---:|
| Best validation epoch | 50 |
| Best validation loss | 75.1559 |
| Test total VAE loss | 74.8792 |
| Test reconstruction loss | 68.5376 |
| Test KL divergence | 6.3416 |

## Latent-neighbor result

The analysis uses 1,000 held-out test molecules as queries and 8,000 training molecules as references.

| Metric | Result |
|---|---:|
| Neighbors per query | 10 |
| Mean nearest-neighbor Tanimoto | 0.2312 |
| Mean random-baseline Tanimoto | 0.0774 |
| Absolute mean improvement | 0.1537 |
| Nearest neighbor beats paired random | 94.94% |
| Pearson distance/similarity correlation | -0.1198 |
| Spearman distance/similarity correlation | -0.1252 |

Latent nearest neighbors are approximately three times more similar than random training molecules according to Morgan-fingerprint Tanimoto similarity.

The weak negative distance/similarity correlations show that the latent space enriches for fingerprint similarity, but Euclidean latent distance is not a strong or complete molecular-similarity measure.

## Current evidence

The repository currently includes:

- reproducible QM9 subset preparation and fingerprint generation;
- deterministic non-overlapping dataset splits;
- a saved best model checkpoint and held-out test metrics;
- deterministic 16-dimensional latent vectors;
- training-fitted PCA and UMAP projections;
- split-colored and molecular-property-colored figures;
- test-to-training latent nearest-neighbor retrieval;
- a deterministic random-similarity baseline;
- quantitative latent-distance and Tanimoto analysis;
- automated tests for artifact and row alignment.

See [PCA_ANALYSIS.md](PCA_ANALYSIS.md), [UMAP_ANALYSIS.md](UMAP_ANALYSIS.md), [PROPERTY_ANALYSIS.md](PROPERTY_ANALYSIS.md), and [LATENT_NEIGHBOR_ANALYSIS.md](LATENT_NEIGHBOR_ANALYSIS.md).

## Known limitations

The current model reconstructs fixed-length Morgan fingerprints rather than molecular graphs or SMILES strings. It therefore cannot directly generate chemically valid molecular structures.

The project has not yet evaluated:

- fingerprint bit-level reconstruction accuracy;
- Tanimoto similarity between original and reconstructed fingerprints;
- reconstruction precision, recall, and F1 score;
- repeated training across multiple random seeds;
- alternative latent dimensions;
- alternative latent-distance metrics;
- alternative model architectures;
- statistical confidence intervals for neighbor evaluation.

Tanimoto similarity measures fingerprint overlap and should not be interpreted as complete chemical, biological, or functional similarity.

## Current work

The latent-neighbor Tanimoto analysis is complete.

For each held-out test molecule, the workflow retrieves ten nearest training molecules in the original 16-dimensional latent space and compares their fingerprints against deterministic random training references.

The results provide quantitative evidence that the learned latent space retains useful local fingerprint information.

## Next planned step

The next branch should evaluate fingerprint reconstruction quality on the held-out test split.

That branch should:

1. load the selected best Fingerprint VAE checkpoint;
2. encode held-out test fingerprints using deterministic latent means;
3. reconstruct fingerprints through the decoder;
4. apply an explicitly configured probability threshold;
5. calculate bit-level accuracy, precision, recall, and F1 score;
6. calculate per-molecule original-versus-reconstructed Tanimoto similarity;
7. compare reconstruction performance with simple sparse-fingerprint baselines;
8. export versioned metrics and figures;
9. document the effect of fingerprint sparsity on metric interpretation.

After reconstruction evaluation, the project should repeat training across multiple seeds and compare alternative latent dimensions.