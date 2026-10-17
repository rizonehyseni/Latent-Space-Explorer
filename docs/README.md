# Documentation Guide

This directory contains the project's technical and research documentation. Features and results are documented only after they have been implemented and verified.

## Documents

| Document | Purpose |
| --- | --- |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Implemented system design, data flow, and current technical boundaries. |
| [METHODOLOGY.md](METHODOLOGY.md) | Data representation, model design, objective, and training approach. |
| [DATASET.md](DATASET.md) | QM9 source, preparation workflow, provenance, and generated artifacts. |
| [RESEARCH_QUESTIONS.md](RESEARCH_QUESTIONS.md) | Scientific questions and the current evidence for each. |
| [DECISIONS.md](DECISIONS.md) | Design decisions, rationale, and trade-offs. |
| [LIMITATIONS.md](LIMITATIONS.md) | Scientific and engineering limitations. |
| [LATENT_EXPORT.md](LATENT_EXPORT.md) | Latent-vector artifact schema, provenance, and reproducible export workflow. |
| [LATENT_SPACE_ANALYSIS.md](LATENT_SPACE_ANALYSIS.md) | Reproducible PCA and UMAP projections, property-colored maps, interpretation, and limitations. |
| [LATENT_NEIGHBOR_ANALYSIS.md](LATENT_NEIGHBOR_ANALYSIS.md) | Quantitative latent-neighbor retrieval and Morgan-fingerprint Tanimoto similarity analysis. |
| [FINGERPRINT_RECONSTRUCTION.md](FINGERPRINT_RECONSTRUCTION.md) | Held-out fingerprint reconstruction metrics, validation-based threshold selection, figures, and limitations. |
| [ROBUSTNESS_ANALYSIS.md](ROBUSTNESS_ANALYSIS.md) | Multi-seed and latent-dimension robustness experiment, results, interpretation, and limitations. |
| [WEB_DATA_EXPORT.md](WEB_DATA_EXPORT.md) | Browser-ready QM9 molecule, neighbor, metrics, and manifest JSON contracts. |
| [Web application](../web/README.md) | Interactive React/Plotly explorer, local setup, features, validation, and scientific boundaries. |
| [EXPERIMENTS.md](EXPERIMENTS.md) | Reproducible records of completed training runs and their interpretation. |
| [REPRODUCIBILITY.md](REPRODUCIBILITY.md) | Environment setup and the full reproduction workflow. |
| [GLOSSARY.md](GLOSSARY.md) | Machine learning and cheminformatics terminology. |
| [FIGURES/README.md](FIGURES/README.md) | Figure index and capture conventions. |

## Reproducibility record

Every retained experiment should identify the dataset source and molecule count, preprocessing settings, configuration path, random seed, Git commit, metrics, interpretation, and limitations.
