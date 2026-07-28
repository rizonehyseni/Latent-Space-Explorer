# Research Questions

This document defines the scientific questions investigated by the Molecular Latent Space Explorer project. The questions are aligned with the current Fingerprint VAE baseline and will evolve as new model representations are introduced.

<details>
<summary>RQ1 - Latent-space structure</summary>

Does the Fingerprint VAE learn a latent representation in which molecules with similar Morgan fingerprints are located near one another?

**Evaluation direction:**

- compare latent-space distance with fingerprint similarity;
- inspect nearest neighbors;
- analyze whether local latent neighborhoods contain chemically related molecules.

</details>

<details>
<summary>RQ2 - Molecular-property organization</summary>

Do molecular properties such as molecular weight, LogP, TPSA, ring count, and heavy-atom count show identifiable patterns across the learned latent space?

**Evaluation direction:**

- project latent vectors using PCA and UMAP;
- color projected points by molecular properties;
- inspect gradients, clusters, and outliers.

</details>

<details>
<summary>RQ3 - Reconstruction quality</summary>

How accurately can a dense Fingerprint VAE reconstruct 2048-bit Morgan fingerprints from a 16-dimensional latent representation?

**Evaluation direction:**

- reconstruction loss;
- fingerprint bit reconstruction accuracy;
- Tanimoto similarity between original and reconstructed fingerprints;
- validation and test-set metrics.

</details>

<details>
<summary>RQ4 - Latent dimensionality</summary>

How does latent dimensionality affect reconstruction quality, latent-space organization, and interpretability?

**Evaluation direction:**

- compare configurations such as 8, 16, 32, and 64 latent dimensions;
- record reconstruction and validation metrics;
- compare projected latent-space structure.

</details>

<details>
<summary>RQ5 - Representation limitations</summary>

What are the practical limitations of a fingerprint-based VAE compared with a future graph-based molecular VAE?

</details>

**Evaluation direction:**

- compare interpretability and neighborhood structure;
- assess whether valid molecular structures can be decoded;
- document differences in computational cost and implementation complexity.

## Current scope

The current project stage addresses the training workflow and validation pipeline required to investigate these questions. Meaningful scientific conclusions will require a larger documented QM9 subset, a held-out test set, and latent-space export.
