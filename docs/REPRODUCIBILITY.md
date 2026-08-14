# Reproducibility Guide

## Purpose

This guide describes how to reproduce the QM9 Fingerprint VAE baseline, deterministic latent-vector export, PCA and UMAP projections, and molecular-property-colored visualizations.

The workflow prepares a deterministic QM9 subset, creates train/validation/test partitions, trains and evaluates the model, exports latent vectors, and generates the documented scientific figures.

## Requirements

- Python 3.12
- PyTorch
- RDKit
- NumPy
- Pandas
- PyYAML
- Matplotlib
- Scikit-learn
- UMAP-learn

Install the project dependencies in an activated virtual environment:

```powershell
pip install -r requirements.txt
```

## 1. Prepare the QM9 subset

Run:

```bash
python -m backend.prepare_qm9
```

This command downloads the QM9 archive when necessary, validates molecules with RDKit, creates canonical SMILES, and writes a deterministic 10,000-molecule subset.

**Expected artifacts:**

- `data/interim/qm9_subset.csv`
- `data/interim/qm9_subset_manifest.json`

## 2. Generate fingerprints and dataset splits

Run:

```bash
python -m backend.run_preprocessing --config configs/qm9_processing.yaml
```

This command creates Morgan fingerprints and deterministic non-overlapping train, validation, and test split indices.

**Expected artifacts:**

- `data/processed/qm9/molecules_metadata.csv`
- `data/processed/qm9/morgan_fingerprints.npy`
- `data/processed/qm9/split_indices.npz`
- `data/processed/qm9/preparation_summary.json`

The default split sizes are:

| Split | Molecules |
|--------|----------:|
| Training | 8,000 |
| Validation | 1,000 |
| Test | 1,000 |

## 3. Run split tests

Run:

```bash
python -m unittest discover -s .\tests -p "test_*.py" -v
```

The tests verify that split generation is deterministic, non-overlapping, and correctly sized.

## 4. Train and evaluate the QM9 baseline

Run:

```bash
python -m backend.run_training --config configs/qm9_fingerprint_vae.yaml
```

The training workflow:

- loads the processed QM9 fingerprints and split indices;
- trains the Fingerprint VAE;
- selects the best checkpoint using validation loss;
- evaluates the selected checkpoint on the held-out test split;
- saves the checkpoint and evaluation metrics.

**Expected artifacts:**

- `models/qm9_fingerprint_vae.pt`
- `models/qm9_fingerprint_vae_results.json`

## 5. Generate the training-history figure

Run:

```bash
python -m backend.plot_training_history
```

**Expected artifact:**

- `docs/FIGURES/qm9-fingerprint-vae-training-curves-v1.png`

## 6. Export deterministic latent vectors

Run:

`python -m backend.export_latent_vectors --config configs/qm9_latent_export.yaml`

Expected artifacts:

- `data/processed/qm9/latent_vectors.npy`
- `data/processed/qm9/latent_metadata.csv`
- `data/processed/qm9/latent_export_manifest.json`

## 7. Generate the PCA projection

Run:

`python -m backend.plot_latent_pca --config configs/qm9_latent_pca.yaml`

Expected artifacts:

- `data/processed/qm9/pca_coordinates.npy`
- `data/processed/qm9/pca_metadata.csv`
- `data/processed/qm9/pca_manifest.json`
- `docs/FIGURES/qm9-latent-pca-by-split-v1.png`

## 8. Generate the UMAP projection

Run:

`python -m backend.plot_latent_umap --config configs/qm9_latent_umap.yaml`

Expected artifacts:

- `data/processed/qm9/umap_coordinates.npy`
- `data/processed/qm9/umap_metadata.csv`
- `data/processed/qm9/umap_manifest.json`
- `docs/FIGURES/qm9-latent-umap-by-split-v1.png`

UMAP is fitted only on the training split and then used to transform validation and test molecules.

## 9. Generate property-colored figures

Run:

`python -m backend.plot_latent_properties --config configs/qm9_property_visualizations.yaml`

Expected artifacts:

- `data/processed/qm9/property_visualization_manifest.json`
- `docs/FIGURES/qm9-latent-pca-by-property-v1.png`
- `docs/FIGURES/qm9-latent-umap-by-property-v1.png`

The workflow validates molecule and property alignment between PCA and UMAP metadata before generating either figure.


## 10. Run the latent-neighbor Tanimoto analysis

Run:

`python -m backend.analyze_latent_neighbors --config configs/qm9_latent_neighbor_tanimoto.yaml`

Expected generated artifacts:

- `data/processed/qm9/latent_neighbor_tanimoto.csv`
- `data/processed/qm9/latent_neighbor_tanimoto_summary.json`
- `docs/FIGURES/qm9-latent-distance-vs-tanimoto-v1.png`
- `docs/FIGURES/qm9-neighbor-tanimoto-vs-random-v1.png`

The analysis uses held-out test molecules as queries, training molecules as references, and the original 16-dimensional latent vectors for nearest-neighbor retrieval.

Expected recorded results:

| Metric | Result |
|---|---:|
| Mean nearest-neighbor Tanimoto | 0.2312 |
| Mean random-baseline Tanimoto | 0.0774 |
| Absolute mean improvement | 0.1537 |
| Nearest neighbor beats paired random | 94.94% |
| Spearman distance/similarity correlation | -0.1252 |

## 11. Run fingerprint reconstruction evaluation

Run:

`python -m backend.evaluate_fingerprint_reconstruction --config configs/qm9_fingerprint_reconstruction.yaml`

The workflow selects the probability threshold using only the validation split and evaluates the selected threshold on the held-out test split.

Expected generated artifacts:

- `data/processed/qm9/fingerprint_reconstruction_per_molecule.csv`
- `data/processed/qm9/fingerprint_reconstruction_summary.json`
- `docs/FIGURES/qm9-fingerprint-reconstruction-metrics-v1.png`
- `docs/FIGURES/qm9-fingerprint-reconstruction-tanimoto-v1.png`

Expected recorded results:

| Metric | Result |
|---|---:|
| Selected threshold | 0.25 |
| Bit accuracy | 0.9915 |
| Precision | 0.6106 |
| Recall | 0.4147 |
| F1 score | 0.4940 |
| Mean Tanimoto | 0.3307 |
| All-zero baseline accuracy | 0.9900 |

## 12. Run the robustness analysis

Run:

`python -m backend.run_robustness_analysis --config configs/qm9_robustness.yaml --execute`

The experiment trains nine models using three random seeds and latent dimensions `8`, `16`, and `32`. Completed runs are reused automatically if execution is interrupted.

Expected generated artifacts:

- individual checkpoints under `models/qm9_robustness/`;
- individual run results under `data/processed/qm9/robustness_runs/`;
- `data/processed/qm9/robustness_summary.json`;
- `docs/FIGURES/qm9-robustness-comparison-v1.png`.

Expected aggregate results:

| Latent dimensions | Reconstruction F1 | Mean Tanimoto |
|---:|---:|---:|
| 8 | 0.4949 ± 0.0118 | 0.3322 ± 0.0110 |
| 16 | 0.4953 ± 0.0034 | 0.3320 ± 0.0034 |
| 32 | 0.4949 ± 0.0098 | 0.3317 ± 0.0090 |

## 13. Export browser-ready QM9 data

Run:

`python -m backend.export_web_data --config configs/qm9_web_export.yaml`

Expected generated artifacts:

- `web/public/data/qm9_molecules.json`
- `web/public/data/qm9_neighbors.json`
- `web/public/data/qm9_metrics.json`
- `web/public/data/qm9_web_export_manifest.json`

The exporter validates PCA and UMAP row alignment, molecule identities, dataset splits, molecular properties, neighbor queries, and training references before writing frontend JSON.

The manifest records file sizes and SHA-256 checksums for all exported browser artifacts.

## 14. Run the backend test suite

Run from the repository root with the virtual environment active:

```powershell
python -m unittest discover -s tests -v
```

The current suite contains 36 passing tests covering dataset splits, latent export, PCA, UMAP, property alignment, neighbor analysis, fingerprint reconstruction, robustness, figure generation, and browser-data export.

## 15. Run and validate the web explorer

Install the frontend dependencies:

```powershell
cd web
npm install
```

Start the development application:

```powershell
npm run dev
```

Validate the production application:

```powershell
npm run lint
npm run build
```

The explorer should load all 10,000 molecules and support PCA/UMAP switching, property coloring, molecule search, dataset filtering, property filtering, molecule inspection, and held-out neighbor comparison.

## Reproducibility notes

Large processed datasets, model checkpoints, and intermediate experiment results are excluded from Git because they are reproducible generated artifacts. The validated browser JSON artifacts under `web/public/data/` are tracked so the interactive explorer can run directly after installing its dependencies.

The repository stores:

- source code;
- configuration files;
- split-generation logic;
- tests;
- documentation;
- the first training-history figure.

The dataset manifest records the source URL, archive checksum, subset size, random seed, rejected-molecule count, and output schema.