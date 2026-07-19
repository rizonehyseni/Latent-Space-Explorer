# Latent Space Explorer: Generative VAE framework for molecular topology

**Can we decode the geometric language of molecular structures?**

Latent Space Explorer is a generative VAE framework designed to navigate the hidden dimensions of chemical space. By mapping complex latent representations into structural reality, the project enables researchers to see and explore what was previously hidden in the data. The project aims to bridge the gap between high-dimensional latent space representation and intuitive 3D molecular topology.

##  Core Architecture
The system employs a **Variational Autoencoder (VAE)** architecture to project molecular data into a continuous latent space. 
By leveraging **RDKit** for molecular graph processing and **Three.js** for real-time volumetric rendering, the framework enables seamless, low-latency interpolation between distinct chemical states.

##  Technical Specifications
- **Generative Modeling:** PyTorch-based VAE, trained on the QM9/ZINC molecular datasets to learn efficient graph latent representations.
- **Backend:** High-throughput API built with FastAPI to handle tensor-based latent projections and property estimation.
- **Frontend:** GPU-accelerated rendering utilizing **React-Three-Fiber** and custom GLSL bloom shaders to facilitate interactive visualization of complex 3D molecular structures.
- **Dynamic Morphing:** Real-time linear and spherical interpolation (SLERP) of latent vectors to observe structural transitions within the chemical space.

##  Development Roadmap
- [ ] **Phase I: Generative Pipeline**
    - [x] CSV-based SMILES ingestion and validation with RDKit.
    - [x] Molecular descriptor extraction, including molecular weight, LogP, TPSA, atom counts, and ring counts.
    - [x] Morgan fingerprint tensorization into fixed-size 2048-bit vectors.
    - [x] Export of processed metadata and fingerprints for model training.
    - [ ] Implementation and training of the VAE architecture.
    - [ ] Latent projection and reconstruction evaluation.
- [ ] **Phase II: Interactive Visualization Layer**
    - [ ] Development of the WebGL-based molecular engine.
    - [ ] Shader-based implementation of post-processing bloom effects for high-fidelity rendering.
- [ ] **Phase III: System Integration & Analysis**
    - [ ] Latent space navigation and property-driven exploration tools.
    - [ ] Optimization of interpolation algorithms for real-time fluidity.

##  Project Objective
To provide a scalable framework for **Explainable AI (XAI)** in computational chemistry, allowing researchers to visualize latent representations and gain insights into structural chemical evolution.

## Current Data Pipeline

The preprocessing pipeline currently uses `data/qm9_sample.csv` as a small development dataset. It validates each SMILES string, calculates molecular descriptors, and produces model-ready Morgan fingerprints.

Run the pipeline from the project root:

```powershell
python -m backend.run_preprocessing
```

Generated artifacts are written to `data/processed/`:

- `molecules_metadata.csv` contains canonical SMILES and molecular properties.
- `morgan_fingerprints.npy` contains the 2048-bit fingerprint matrix used as the VAE input.

The next milestone is training a VAE on a substantially larger QM9 dataset subset; the three-molecule sample is intended only to validate the pipeline.

---
*License: MIT*
