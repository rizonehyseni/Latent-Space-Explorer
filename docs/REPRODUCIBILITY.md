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

## 10. Run the complete test suite

Run:

`python -m unittest discover -s tests -p "test_*.py" -v`


## Expected baseline result

The first recorded QM9 baseline used 50 training epochs.

| Metric | Result |
|--------|-------:|
| Best validation epoch | 50 |
| Best validation loss | 75.1559 |
| Test total VAE loss | 74.8792 |
| Test reconstruction loss | 68.5376 |
| Test KL divergence | 6.3416 |

Small numeric differences may occur when package versions, hardware, or floating-point behavior differ.

## Reproducibility notes

The generated datasets, model checkpoints, and result JSON files are excluded from Git because they are generated artifacts.

The repository stores:

- source code;
- configuration files;
- split-generation logic;
- tests;
- documentation;
- the first training-history figure.

The dataset manifest records the source URL, archive checksum, subset size, random seed, rejected-molecule count, and output schema.