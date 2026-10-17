# Research Questions

This document defines the scientific questions investigated by the Latent Space Explorer project. The questions are aligned with the current Fingerprint VAE baseline and will evolve as new model representations are introduced.

<details>
<summary><h3>RQ1 - Latent-space structure</h3></summary>

Does the Fingerprint VAE learn a latent representation in which molecules with similar Morgan fingerprints are located near one another?

**Evaluation direction:**

- compare latent-space distance with fingerprint similarity;
- inspect nearest neighbors;
- analyze whether local latent neighborhoods contain chemically related molecules.

</details>

<details>
<summary><h3>RQ2 - Molecular-property organization</h3></summary>

Do molecular properties such as molecular weight, LogP, TPSA, ring count, and heavy-atom count show identifiable patterns across the learned latent space?

**Evaluation direction:**

- project latent vectors using PCA and UMAP;
- color projected points by molecular properties;
- inspect gradients, clusters, and outliers.

</details>

<details>
<summary><h3>RQ3 - Reconstruction quality</h3></summary>

How accurately can a dense Fingerprint VAE reconstruct 2048-bit Morgan fingerprints from a 16-dimensional latent representation?

**Evaluation direction:**

- reconstruction loss;
- fingerprint bit reconstruction accuracy;
- Tanimoto similarity between original and reconstructed fingerprints;
- validation and test-set metrics.

</details>

<details>
<summary><h3>RQ4 - Latent dimensionality</h3></summary>

How does latent dimensionality affect reconstruction quality, latent-space organization, and interpretability?

**Evaluation direction:**

- compare configurations with 8, 16, and 32 latent dimensions;
- record reconstruction and validation metrics;
- compare projected latent-space structure.

</details>

<details>
<summary><h3>RQ5 - Representation limitations</h3></summary>

What are the practical limitations of a fingerprint-based VAE compared with a future graph-based molecular VAE?



**Evaluation direction:**

- compare interpretability and neighborhood structure;
- assess whether valid molecular structures can be decoded;
- document differences in computational cost and implementation complexity.
</details>

## Current answers

The QM9 Fingerprint VAE baseline and its follow-up analyses provide the following evidence. All results use the deterministic 10,000-molecule subset with 8,000 training, 1,000 validation, and 1,000 held-out test molecules.

| Question | Status | Evidence |
|---|---|---|
| RQ1 - Latent-space structure | Partly answered | Nearest latent neighbors have a mean Tanimoto similarity of 0.2312, compared with 0.0774 for random training molecules, and beat the paired random reference for 94.94% of test queries. The Spearman correlation between latent distance and Tanimoto similarity is only -0.1252, so proximity is informative but not a complete similarity measure. See [LATENT_NEIGHBOR_ANALYSIS.md](LATENT_NEIGHBOR_ANALYSIS.md). |
| RQ2 - Molecular-property organization | Exploratory evidence | Property-colored PCA and UMAP maps show systematic variation in TPSA, ring count, and LogP across parts of the projections. The figures do not measure statistical significance. See [LATENT_SPACE_ANALYSIS.md](LATENT_SPACE_ANALYSIS.md). |
| RQ3 - Reconstruction quality | Answered for the baseline | With a validation-selected threshold of 0.25, held-out reconstruction reaches an F1 score of 0.4940 and a mean Tanimoto similarity of 0.3307. Bit accuracy of 0.9915 is close to the all-zero baseline of 0.9900 because fingerprints are sparse. See [FINGERPRINT_RECONSTRUCTION.md](FINGERPRINT_RECONSTRUCTION.md). |
| RQ4 - Latent dimensionality | Answered for reconstruction | Across three seeds, 8, 16, and 32 latent dimensions give a mean reconstruction F1 of about 0.495. The 16-dimensional model shows the lowest seed-to-seed variation. The effect of dimensionality on latent organization has not been compared. See [ROBUSTNESS_ANALYSIS.md](ROBUSTNESS_ANALYSIS.md). |
| RQ5 - Representation limitations | Open | No graph-based model has been implemented, so the comparison with a graph VAE remains future work. The fingerprint model cannot decode valid molecular structures. See [LIMITATIONS.md](LIMITATIONS.md). |
