  <h1 align="center">Latent Space Explorer: Generative VAE framework for molecular topology</h1>
  
**Can we decode the geometric language of molecular structures?**

Latent Space Explorer is a molecular machine-learning project that maps chemical fingerprints into a continuous latent space. The current implementation establishes a configurable Fingerprint VAE baseline; later phases will connect its latent representations to an interactive 3D explorer.

##  Core Architecture
The implemented pipeline uses **RDKit** to validate SMILES strings, calculate descriptors, and create 2048-bit Morgan fingerprints. A PyTorch **dense VAE** compresses those fingerprints into a 16-dimensional latent vector and reconstructs fingerprint logits using the reparameterization trick.

The React/Vite application is currently a frontend scaffold. Three.js rendering, a browser data pipeline, latent-vector export, and interpolation controls are planned but are not implemented yet.

### Why Latent Spaces?
At the heart of this project lies the **Latent Space**, a compressed representation of chemical structures. Instead of treating molecules as static, discrete data points, the VAE learns to map complex molecular fingerprints into a continuous 16-dimensional coordinate system. 

- **Feature Compression:** We distill massive chemical data into meaningful geometric patterns.
- **Continuous Exploration:** By moving through this latent space, we can perform "interpolation," transitioning smoothly between different molecular structures to observe how chemical properties evolve.
- **Explainable Discovery:** This space serves as our canvas, allowing researchers to identify regions of chemical space that may contain undiscovered compounds with specific characteristics.

<div align=center> <img width="720" height="315" alt="6437e8cb4769a16c5e8b05df_vwvyaj5kzubtpztsq30gubgjbumdkrno_cb57s6bukovkyhcnwzktorvcr8-skmgvobh8mf--_bq2k0hhftkqsejkg_slihkxtzyawtn1lrptioxg10jsdg8ijbgtq6wvtfx5gdubry0e6jwq9p4za" src="https://github.com/user-attachments/assets/af9f4f77-6041-4a5b-9c94-5fb2c7575f6b" /> </div>
<div align="center">
<small>Figure: Conceptual latent-space encoder-decoder illustration. It is not the current model architecture. Adapted from <a href="https://hackernoon.com/latent-space-visualization-deep-learning-bits-2-bd09a46920df">HackerNoon</a>.</small>
</div>


## Current implementation

- **Preprocessing:** RDKit SMILES validation, canonicalization, descriptor extraction, and 2048-bit Morgan fingerprints.
- **Generative model:** PyTorch dense/MLP VAE with a 16-dimensional latent space.
- **Loss:** Binary cross-entropy with logits for reconstruction plus KL divergence.
- **Experiment configuration:** YAML selects the dataset path, model dimensions, training hyperparameters, seed, and checkpoint path.
- **Validation:** A deterministic train/validation split reports evaluation-only validation loss, reconstruction loss, and KL divergence after every epoch.
- **Artifacts:** processed metadata and fingerprints in `data/processed/`; model checkpoint and per-epoch training history in `models/molecular_vae.pt`.
- **Frontend:** React/Vite scaffold only; it is not yet connected to model artifacts or a rendering library.

This is a fingerprint-based baseline, not a convolutional or graph VAE. It reconstructs molecular fingerprint features; it does not decode latent vectors directly into chemically valid SMILES or molecular graphs.

##  Development Roadmap
- [ ] **Phase I: Fingerprint VAE baseline**
    - [x] CSV-based SMILES ingestion and validation with RDKit.
    - [x] Molecular descriptor extraction, including molecular weight, LogP, TPSA, atom counts, and ring counts.
    - [x] Morgan fingerprint tensorization into fixed-size 2048-bit vectors.
    - [x] Export of processed metadata and fingerprints for model training.
    - [x] Dense VAE architecture, reparameterization, loss function, and training entry point.
    - [x] YAML-based experiment configuration for reproducible training settings.
    - [x] Deterministic train/validation split and validation metrics.
    - [ ] Train and evaluate on a substantially larger dataset with train/validation/test splits.
    - [ ] Export latent vectors and reconstruction metrics.
- [ ] **Phase II: Interactive visualization**
    - [ ] Export 3D display coordinates and metadata for the browser.
    - [ ] Replace the React starter screen with a molecular point-cloud explorer.
    - [ ] Add selection, descriptor filters, and molecule detail panels.
- [ ] **Phase III: Advanced molecular representations**
    - [ ] Evaluate a graph VAE or, if an appropriate spatial input representation is chosen, a convolutional VAE.
    - [ ] Add latent-space interpolation and assess chemical validity of decoded results.

##  Project Objective
To provide a scalable framework for **Explainable AI (XAI)** in computational chemistry, allowing researchers to visualize latent representations and gain insights into structural chemical evolution.

## Current Data Pipeline

The preprocessing pipeline currently uses `data/qm9_sample.csv` as a small development dataset. It validates each SMILES string, calculates molecular descriptors, and produces model-ready Morgan fingerprints. The sample is intended to validate the pipeline, not to train or evaluate a scientific model.

Run the pipeline from the project root:

```powershell
python -m backend.run_preprocessing
```

Generated artifacts are written to `data/processed/`:

- `molecules_metadata.csv` contains canonical SMILES and molecular properties.
- `morgan_fingerprints.npy` contains the 2048-bit fingerprint matrix used as the VAE input.

## Training the Fingerprint VAE

After preprocessing, run the default experiment configuration:

```powershell
python -m backend.run_training
```

The default settings are in `configs/fingerprint_vae.yaml`: a 16-dimensional latent space, batch size 64, Adam with learning rate 0.001, and 50 epochs. Training automatically uses CUDA when available and writes the resulting checkpoint to `models/molecular_vae.pt`.

To run a different experiment configuration, pass its path explicitly:

```powershell
python -m backend.run_training --config path/to/experiment.yaml
```

For the detailed architecture, project progress, and recorded training runs, see [docs/README.md](docs/README.md).

---
*License: MIT*
