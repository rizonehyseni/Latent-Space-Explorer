# Methodology

## Overview
<div align="justify">
The Molecular Latent Space Explorer currently implements a **Fingerprint Variational Autoencoder (VAE) baseline**.

The workflow transforms molecular SMILES strings into fixed-length Morgan fingerprints, compresses them into a 16-dimensional latent representation, and reconstructs the fingerprint representation.

```mermaid
flowchart TD
    A["SMILES and QM9 metadata"] --> B["RDKit validation<br/>Canonicalization"]
    B --> C["Molecular descriptors<br/>Morgan fingerprints"]

    C --> D["Fingerprint VAE encoder"]
    D --> E["Latent distribution<br/>μ and log variance"]
    E --> F["Sampled latent vector z"]
    F --> G["Decoder"]
    G --> H["Reconstruction logits"]
    H --> I["VAE training objective<br/>BCE with logits + KL divergence"]

    E --> J["Deterministic latent mean<br/>μ ∈ R¹⁶"]
    J --> K["PCA projection"]
    J --> L["UMAP projection"]

    C --> M["Aligned molecular properties"]
    K --> N["Property-colored PCA"]
    L --> O["Property-colored UMAP"]
    M --> N
    M --> O

    J --> P["16D nearest-neighbor retrieval"]
    C --> Q["Morgan fingerprints"]
    P --> R["Latent distance and<br/>Tanimoto comparison"]
    Q --> R
    R --> S["Random-baseline comparison"]
```

---

# Molecular Preprocessing

## Input Data

The input data is provided as a CSV file containing a required:

```text
smiles
```

column.

The preprocessing pipeline performs the following steps:

1. Reads the source CSV file.
2. Validates each SMILES string using RDKit.
3. Removes invalid molecules.
4. Creates canonical SMILES representations.
5. Calculates molecular descriptors.
6. Generates Morgan fingerprints.
7. Saves metadata and fingerprint artifacts.

---

## Molecular Descriptors

The preprocessing stage extracts molecular descriptors used for analysis and visualization.

| Descriptor | Description |
|---|---|
| Molecular weight | Total molecular mass of the molecule |
| LogP | Estimate of molecular lipophilicity |
| Atom count | Total number of atoms |
| Heavy-atom count | Number of non-hydrogen atoms |
| Hydrogen-bond donor count | Number of hydrogen-bond donor groups |
| Hydrogen-bond acceptor count | Number of hydrogen-bond acceptor groups |
| Topological polar surface area (TPSA) | Descriptor related to molecular polarity |
| Ring count | Number of molecular rings |

These descriptors are not used as direct inputs to the VAE. They are preserved as molecular metadata for later analysis of the learned latent space.

---

# Morgan Fingerprints

Each valid molecule is transformed into a **2048-bit Morgan fingerprint**.

The current implementation uses:

```text
Radius: 2
Fingerprint size: 2048 bits
```

Morgan fingerprints represent molecular structures as fixed-dimensional binary vectors.

Formally, each molecule is transformed into:

$$
x \in \{0,1\}^{2048}
$$

where each element represents the presence or absence of a hashed molecular substructure.

Morgan fingerprints are suitable for the current baseline because they are:

- Compact.
- Computationally efficient.
- Widely used in cheminformatics.

However, they have an important limitation:

> Morgan fingerprints do not contain enough structural information to directly decode a chemically valid molecular graph.

Therefore, the current model learns a latent representation of fingerprint space rather than directly generating molecular structures.

---

# Dense Fingerprint VAE

The current VAE architecture is:

```mermaid
flowchart LR
    A["Morgan fingerprint<br/>x ∈ {0,1}²⁰⁴⁸"] --> B["Encoder"]

    subgraph ENC["Encoder network"]
        B --> C["Linear 2048→512<br/>ReLU"]
        C --> D["Linear 512→128<br/>ReLU"]
    end

    D --> E["Latent distribution"]

    subgraph LAT["Latent space"]
        E --> F["μ ∈ R¹⁶"]
        E --> G["log σ² ∈ R¹⁶"]
        F --> H["Sampling<br/>z = μ + σϵ"]
        G --> H
    end

    H --> I["Decoder"]
    F -->|"Deterministic evaluation"| I
    F --> N["Deterministic latent export<br/>μ ∈ R¹⁶"]

    subgraph DEC["Decoder network"]
        I --> J["Linear 16→128<br/>ReLU"]
        J --> K["Linear 128→512<br/>ReLU"]
        K --> L["Linear 512→2048"]
    end

    L --> M["Reconstruction logits<br/>ℓ ∈ R²⁰⁴⁸"]
    A --> O["Binary cross-entropy<br/>with logits"]
    M --> O

```

The encoder maps the original fingerprint representation into a lower-dimensional latent representation:

$$
x \in \{0,1\}^{2048}
\rightarrow
z \in \mathbb{R}^{16}
$$

where:

- \(x\) is the input Morgan fingerprint.
- \(z\) is the learned latent representation.

---

# Latent Representation and Reparameterization

The encoder does not directly output a single latent vector.

Instead, it learns the parameters of a probability distribution:

$$
q_\phi(z|x)=\mathcal{N}(z;\mu,\sigma^2)
$$

where:

- $\mu$ represents the latent mean vector.
- $\sigma^2$ represents the latent variance.
- $q_\phi(z|x)$ represents the learned latent distribution.

The latent vector is sampled using the reparameterization trick:

$$
z = \mu + \sigma \odot \epsilon
$$

where:

$$
\epsilon \sim \mathcal{N}(0,I)
$$

This allows gradients to flow through the stochastic sampling process during training.

---

# VAE Objective Function

The VAE is trained by minimizing a combination of reconstruction loss and KL divergence:

$$  \mathcal{L}_{VAE}=
\mathcal{L}_{reconstruction}
+
\beta\mathcal{L}_{KL}
$$

where:

- $L_{reconstruction}$ measures how accurately the original molecular fingerprint is reconstructed by the decoder.
- $L_{KL}$ regularizes the latent distribution and encourages the latent space to follow a structured normal distribution.
- $\beta$ controls the contribution of the KL divergence term in the total VAE objective.


For the current implementation:

$$
\beta = 1
$$

---

# Reconstruction Loss

The reconstruction loss is calculated using binary cross-entropy with logits between the original fingerprint and reconstructed fingerprint output.

The binary cross-entropy formulation is:

$$ \mathcal{L}_{reconstruction}=
-\sum_{i=1}^{n}
\left[
x_i\log(\hat{x_i})
+
(1-x_i)\log(1-\hat{x_i})
\right]
$$

where:

- $x_i$ represents the original fingerprint bit.
- $\hat{x_i}$ represents the reconstructed fingerprint probability.

The reconstruction term encourages the decoder to preserve molecular fingerprint information.

---

# KL Divergence

The KL divergence term encourages the learned latent distribution to approximate a standard normal distribution:

$$ \mathcal{L}_{KL}=
D_{KL}
\left(
q_\phi(z|x)
\parallel
p(z)
\right)
$$

For a Gaussian latent distribution, the closed-form expression becomes:

$$
\mathcal{L}_{KL} =
-\frac{1}{2}
\sum_{i=1}^{d}
\left(
1+\log(\sigma_i^2)-\mu_i^2-\sigma_i^2
\right)
$$

where:

- $d$ is the latent dimension.
- $\mu_i$ is the latent mean for dimension $i$.
- $\sigma_i^2$ is the latent variance for dimension $i$.

Together, reconstruction loss and KL divergence encourage the model to:

- Preserve molecular fingerprint information.
- Learn a continuous latent representation.
- Organize molecules into a structured latent space.

---

## QM9 baseline training and evaluation

The first controlled experiment uses a deterministic 10,000-molecule QM9 subset.

The processed dataset is divided into non-overlapping partitions:

| Split | Molecules | Purpose |
|---|---:|---|
| Training | 8,000 | Learn model parameters |
| Validation | 1,000 | Select the best checkpoint |
| Test | 1,000 | Final held-out evaluation |

The model is trained for 50 epochs.

At each epoch, training and validation total VAE loss, reconstruction loss, and KL divergence are recorded.

The checkpoint with the lowest validation loss is retained. After training is complete, that checkpoint is evaluated once on the held-out test split.

## Current evaluation metrics

The first baseline records:

- total VAE loss;
- reconstruction loss;
- KL divergence;
- training and validation curves;
- final held-out test metrics.

The current baseline does not yet measure fingerprint bit-level accuracy or Tanimoto similarity. These metrics are planned for future latent-space and reconstruction-quality evaluation.


## Baseline interpretation

The first baseline demonstrates that the project can complete a reproducible end-to-end experiment from QM9 source preparation to held-out evaluation.

However, decreasing VAE loss alone does not prove that the latent space is chemically meaningful.

The next stage must export latent vectors and evaluate whether molecules that are nearby in latent space also share fingerprint similarity or molecular-property patterns.

## Training Workflow

The dataset is divided into deterministic training and validation subsets using the configured random seed.

During each epoch:

1. The model updates parameters using training batches.
2. Total loss, reconstruction loss, and KL divergence are recorded.
3. Validation data is evaluated without gradient updates.
4. Validation metrics are recorded.
5. Training history and configuration metadata are saved in the checkpoint.

The saved checkpoint contains:

- Model parameters.
- Experiment configuration.
- Dataset split information.
- Training history.
- Random seed.

---

# Current Evaluation Scope

The current three-molecule development sample verifies that:

- Molecular preprocessing executes correctly.
- Morgan fingerprint generation works.
- The VAE training workflow runs end-to-end.
- Validation evaluation functions correctly.
- Checkpoint generation works.

However, this dataset does **not** support scientific conclusions about:

- Model generalization.
- Molecular clustering.
- Reconstruction quality.
- Chemical interpretation of the latent space.

A scientifically meaningful evaluation requires:

- A larger documented QM9 subset.
- Train/validation/test splits.
- Held-out test evaluation.
- Comparison between different model configurations.
- Analysis of latent-space organization.

</div>
