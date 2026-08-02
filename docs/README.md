# Documentation Guide

This directory is the project’s technical and research record. Documentation is updated only when the related implementation or experiment exists.

## Documents

| Document | Purpose |
| --- | --- |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Implemented system design, data flow, and current technical boundaries. |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | Completed milestones, current phase, and planned sequence. |
| [LATENT_EXPORT.md](LATENT_EXPORT.md) | Latent-vector artifact schema, provenance, and reproducible export workflow. |
| [PCA_ANALYSIS.md](PCA_ANALYSIS.md) | Reproducible PCA projection, result, interpretation, and limitations. |
| [UMAP_ANALYSIS.md](UMAP_ANALYSIS.md) | Reproducible UMAP projection, nonlinear latent-space interpretation, PCA comparison, and limitations. |
| [PROPERTY_ANALYSIS.md](PROPERTY_ANALYSIS.md) | Molecular-property-colored PCA and UMAP visualizations, interpretation, and limitations. |
| [LATENT_NEIGHBOR_ANALYSIS.md](LATENT_NEIGHBOR_ANALYSIS.md) | Quantitative latent-neighbor retrieval and Morgan-fingerprint Tanimoto similarity analysis. |
| [EXPERIMENTS.md](EXPERIMENTS.md) | Reproducible records of completed training runs and their interpretation. |
| [FIGURES/README.md](FIGURES/README.md) | Figure, screenshot, and video capture conventions. |

## Documentation rule for each completed feature

When a feature branch delivers working behavior, update only the documents affected by that behavior:

1. Update `ARCHITECTURE.md` if the system flow, data contract, or component responsibilities changed.
2. Update `PROJECT_STATUS.md` when a milestone is completed or the next milestone changes.
3. Add an entry to `EXPERIMENTS.md` when a training run produces a result worth retaining.
4. Save a figure or short recording only when it demonstrates a meaningful result or interaction.

Do not document planned functionality as implemented functionality.

## Reproducibility record

Every retained experiment should identify the dataset source and molecule count, preprocessing settings, configuration path, random seed, Git commit, metrics, interpretation, and limitations.
