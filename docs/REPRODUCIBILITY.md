# Reproducibility Guide

## Purpose

This guide describes how to reproduce every documented result: the QM9 Fingerprint VAE baseline, deterministic latent-vector export, PCA and UMAP projections, property-colored visualizations, latent-neighbor and reconstruction evaluations, the robustness analysis, and the browser data used by the web explorer.

The workflow prepares a deterministic QM9 subset, creates train/validation/test partitions, trains and evaluates the model, exports latent vectors, generates the documented scientific figures, and exports the browser data.

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

```bash
pip install -r requirements.txt
```

The documented experiments ran on CPU. On Linux, `pip` installs the larger CUDA build of PyTorch by default. To use the CPU-only build, install PyTorch from the CPU index before installing the remaining requirements:

```bash
pip install torch==2.13.0 --index-url https://download.pytorch.org/whl/cpu
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
python -m unittest tests.test_splits -v
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

```bash
python -m backend.export_latent_vectors --config configs/qm9_latent_export.yaml
```

Expected artifacts:

- `data/processed/qm9/latent_vectors.npy`
- `data/processed/qm9/latent_metadata.csv`
- `data/processed/qm9/latent_export_manifest.json`

## 7. Generate the PCA projection

Run:

```bash
python -m backend.plot_latent_pca --config configs/qm9_latent_pca.yaml
```

Expected artifacts:

- `data/processed/qm9/pca_coordinates.npy`
- `data/processed/qm9/pca_metadata.csv`
- `data/processed/qm9/pca_manifest.json`
- `docs/FIGURES/qm9-latent-pca-by-split-v1.png`

## 8. Generate the UMAP projection

Run:

```bash
python -m backend.plot_latent_umap --config configs/qm9_latent_umap.yaml
```

Expected artifacts:

- `data/processed/qm9/umap_coordinates.npy`
- `data/processed/qm9/umap_metadata.csv`
- `data/processed/qm9/umap_manifest.json`
- `docs/FIGURES/qm9-latent-umap-by-split-v1.png`

UMAP is fitted only on the training split and then used to transform validation and test molecules.

## 9. Generate property-colored figures

Run:

```bash
python -m backend.plot_latent_properties --config configs/qm9_property_visualizations.yaml
```

Expected artifacts:

- `data/processed/qm9/property_visualization_manifest.json`
- `docs/FIGURES/qm9-latent-pca-by-property-v1.png`
- `docs/FIGURES/qm9-latent-umap-by-property-v1.png`

The workflow validates molecule and property alignment between PCA and UMAP metadata before generating either figure.


## 10. Run the latent-neighbor Tanimoto analysis

Run:

```bash
python -m backend.analyze_latent_neighbors --config configs/qm9_latent_neighbor_tanimoto.yaml
```

Expected generated artifacts:

- `data/processed/qm9/latent_neighbor_tanimoto.csv`
- `data/processed/qm9/latent_neighbor_tanimoto_summary.json`
- `docs/FIGURES/qm9-latent-distance-vs-tanimoto-v1.png`
- `docs/FIGURES/qm9-neighbor-tanimoto-vs-random-v1.png`

The analysis uses held-out test molecules as queries, training molecules as references, and the original 16-dimensional latent vectors for nearest-neighbor retrieval.

Compare the generated summary with the recorded results in [LATENT_NEIGHBOR_ANALYSIS.md](LATENT_NEIGHBOR_ANALYSIS.md).

## 11. Run fingerprint reconstruction evaluation

Run:

```bash
python -m backend.evaluate_fingerprint_reconstruction --config configs/qm9_fingerprint_reconstruction.yaml
```

The workflow selects the probability threshold using only the validation split and evaluates the selected threshold on the held-out test split.

Expected generated artifacts:

- `data/processed/qm9/fingerprint_reconstruction_per_molecule.csv`
- `data/processed/qm9/fingerprint_reconstruction_summary.json`
- `docs/FIGURES/qm9-fingerprint-reconstruction-metrics-v1.png`
- `docs/FIGURES/qm9-fingerprint-reconstruction-tanimoto-v1.png`

Compare the generated summary with the recorded results in [FINGERPRINT_RECONSTRUCTION.md](FINGERPRINT_RECONSTRUCTION.md).

## 12. Run the robustness analysis

Run:

```bash
python -m backend.run_robustness_analysis --config configs/qm9_robustness.yaml --execute
```

The experiment trains nine models using three random seeds and latent dimensions `8`, `16`, and `32`. Completed runs are reused automatically if execution is interrupted.

Expected generated artifacts:

- individual checkpoints under `models/qm9_robustness/`;
- individual run results under `data/processed/qm9/robustness_runs/`;
- `data/processed/qm9/robustness_summary.json`;
- `docs/FIGURES/qm9-robustness-comparison-v1.png`.

Compare the generated summary with the recorded results in [ROBUSTNESS_ANALYSIS.md](ROBUSTNESS_ANALYSIS.md).

## 13. Export browser-ready QM9 data

Run:

```bash
python -m backend.export_web_data --config configs/qm9_web_export.yaml
```

Expected generated artifacts:

- `web/public/data/qm9_molecules.json`
- `web/public/data/qm9_neighbors.json`
- `web/public/data/qm9_metrics.json`
- `web/public/data/qm9_web_export_manifest.json`

The exporter validates PCA and UMAP row alignment, molecule identities, dataset splits, molecular properties, neighbor queries, and training references before writing frontend JSON.

The manifest records file sizes and SHA-256 checksums for all exported browser artifacts.

## 14. Run the backend test suite

Run from the repository root with the virtual environment active:

```bash
python -m unittest discover -s tests -v
```

The suite contains 36 tests covering dataset splits, latent export, PCA, UMAP, property alignment, neighbor analysis, fingerprint reconstruction, robustness, figure generation, and browser-data export. The tests use small synthetic data, so they do not need the generated pipeline artifacts. GitHub Actions runs them on Python 3.12 for every pull request.

## 15. Run and validate the web explorer

The web explorer requires Node.js 20.19+ or 22.12+. Install the frontend dependencies:

```bash
cd web
npm ci
```

Start the development application:

```bash
npm run dev
```

Validate the production application:

```bash
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
- all documented figures in `docs/FIGURES/`;
- the validated browser data in `web/public/data/`.

The dataset manifest records the source URL, archive checksum, subset size, random seed, rejected-molecule count, and output schema.