# Documentation Guide

This directory contains the technical, scientific, and reproducibility record for Latent Space Explorer. Results are documented only after they have been implemented and verified.

## System and methodology

| Document | Purpose |
| --- | --- |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Implemented system design, data flow, and current technical boundaries. |
| [METHODOLOGY.md](METHODOLOGY.md) | Dataset representation, model design, training protocol, and evaluation strategy. |
| [DATASET.md](DATASET.md) | QM9 source, deterministic subset construction, provenance, and split policy. |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | Completed milestones, current phase, and planned sequence. |
| [DECISIONS.md](DECISIONS.md) | Important design choices, rationale, and trade-offs. |
| [LIMITATIONS.md](LIMITATIONS.md) | Scientific and implementation limitations. |
| [RESEARCH_QUESTIONS.md](RESEARCH_QUESTIONS.md) | Questions used to organize the evaluation. |

## Analyses and results

| Document | Purpose |
| --- | --- |
| [LATENT_EXPORT.md](LATENT_EXPORT.md) | Latent-vector artifact schema, provenance, and reproducible export workflow. |
| [PCA_ANALYSIS.md](PCA_ANALYSIS.md) | Reproducible PCA projection, result, interpretation, and limitations. |
| [UMAP_ANALYSIS.md](UMAP_ANALYSIS.md) | Reproducible UMAP projection, nonlinear latent-space interpretation, PCA comparison, and limitations. |
| [PROPERTY_ANALYSIS.md](PROPERTY_ANALYSIS.md) | Molecular-property-colored PCA and UMAP visualizations, interpretation, and limitations. |
| [LATENT_NEIGHBOR_ANALYSIS.md](LATENT_NEIGHBOR_ANALYSIS.md) | Quantitative latent-neighbor retrieval and Morgan-fingerprint Tanimoto similarity analysis. |
| [FINGERPRINT_RECONSTRUCTION.md](FINGERPRINT_RECONSTRUCTION.md) | Held-out fingerprint reconstruction metrics, validation-based threshold selection, figures, and limitations. |
| [ROBUSTNESS_ANALYSIS.md](ROBUSTNESS_ANALYSIS.md) | Multi-seed and latent-dimension robustness experiment, results, interpretation, and limitations. |
| [WEB_DATA_EXPORT.md](WEB_DATA_EXPORT.md) | Browser-ready QM9 molecule, neighbor, metrics, and manifest JSON contracts. |
| [EXPERIMENTS.md](EXPERIMENTS.md) | Reproducible records of completed training runs and their interpretation. |

## Reproducibility and reference

| Document | Purpose |
| --- | --- |
| [REPRODUCIBILITY.md](REPRODUCIBILITY.md) | End-to-end commands for reproducing data, training, analyses, exports, and tests. |
| [GLOSSARY.md](GLOSSARY.md) | Definitions of machine-learning, visualization, and cheminformatics terms. |
| [FIGURES/README.md](FIGURES/README.md) | Figure, screenshot, and video capture conventions. |
| [Web application](../web/README.md) | Interactive React/Plotly explorer, local setup, features, validation, and scientific boundaries. |

## Maintenance rule

When implemented behavior changes:

1. Update `ARCHITECTURE.md` if the system flow, data contract, or component responsibilities changed.
2. Update `METHODOLOGY.md` when the scientific procedure changes.
3. Update `PROJECT_STATUS.md` when a milestone or release state changes.
4. Add an `EXPERIMENTS.md` entry when a retained run produces reportable evidence.
5. Update `REPRODUCIBILITY.md` whenever commands, dependencies, or artifact paths change.
6. Save a figure or recording only when it communicates a meaningful result or interaction.

Do not document planned functionality as implemented functionality.

## Reproducibility record

Every retained experiment should identify the dataset source and molecule count, preprocessing settings, configuration path, random seed, Git commit, metrics, interpretation, and limitations.
