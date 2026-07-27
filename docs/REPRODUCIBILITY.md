# Reproducibility Guide

This guide describes how to reproduce the current Fingerprint VAE development workflow.

---

## Current Scope

The current workflow uses the small tracked development dataset:

```text
data/qm9_sample.csv
```

This dataset is intended to verify the data pipeline and training workflow. It is **not intended for scientific model evaluation**.

---

## Environment Setup

### 1. Create and activate a virtual environment

Create the environment:

```bash
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

---

### 2. Install project dependencies

Install the required packages:

```bash
python -m pip install -r requirements.txt
```

If YAML support is missing, install PyYAML:

```bash
python -m pip install PyYAML
```

---

### 3. Record the Python version

For retained experiments, record the Python version used:

```bash
python --version
```

---

# Preprocess the Development Dataset

Run the preprocessing pipeline:

```bash
python -m backend.run_preprocessing
```

The expected generated artifacts are:

```text
data/processed/molecules_metadata.csv
data/processed/morgan_fingerprints.npy
```

The terminal output should report:

- Valid molecule count
- Rejected molecule count
- Fingerprint matrix shape
- Fingerprint width
- Output directory

---

# Train the Fingerprint VAE

Run the default configured experiment:

```bash
python -m backend.run_training
```

The default configuration file is:

```text
configs/fingerprint_vae.yaml
```

The training run should report:

- Selected device (CPU/CUDA)
- Total molecule count
- Training molecule count
- Validation molecule count
- Latent dimension
- Training metrics for each epoch
- Validation metrics for each epoch
- Checkpoint output path

The generated checkpoint is saved to:

```text
models/molecular_vae.pt
```

---

# Run a Different Configuration

A custom YAML configuration can be provided:

```bash
python -m backend.run_training --config path/to/experiment.yaml
```

Each retained experiment should preserve:

- The configuration file
- The Git commit hash
- The dataset source and size
- The random seed
- Relevant terminal output
- Generated figures
- Written interpretation in:

```text
docs/EXPERIMENTS.md
```

---

# Current Reproducibility Limitation

The current development sample contains only three molecules.

Reproducing this workflow confirms that:

- The data pipeline functions correctly
- The preprocessing stage executes successfully
- The VAE training workflow runs end-to-end

However, it **does not reproduce a scientifically meaningful molecular-learning experiment**.

A future QM9 workflow should document:

- Dataset source and version
- Preprocessing rules
- Train/validation/test split sizes
- Evaluation metrics on held-out test data
- Experimental comparisons between model configurations
