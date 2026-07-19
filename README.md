# Latent Space Explorer: Generative VAE framework for molecular topology

**Latent Space Explorer** is a generative framework designed for the visualization and exploration of chemical molecular manifolds. The project aims to bridge the gap between high-dimensional latent space representation and intuitive 3D molecular topology.

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
    - [ ] Implementation of the VAE architecture and latent projection pipeline.
    - [ ] Pre-processing and tensorization of molecular graph structures via RDKit.
- [ ] **Phase II: Interactive Visualization Layer**
    - [ ] Development of the WebGL-based molecular engine.
    - [ ] Shader-based implementation of post-processing bloom effects for high-fidelity rendering.
- [ ] **Phase III: System Integration & Analysis**
    - [ ] Latent space navigation and property-driven exploration tools.
    - [ ] Optimization of interpolation algorithms for real-time fluidity.

##  Project Objective
To provide a scalable framework for **Explainable AI (XAI)** in computational chemistry, allowing researchers to visualize latent representations and gain insights into structural chemical evolution.

---
*License: MIT*
