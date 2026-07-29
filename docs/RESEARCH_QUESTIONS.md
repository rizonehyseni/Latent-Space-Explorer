# Research Questions

This document defines the scientific questions investigated by the Molecular Latent Space Explorer project. The questions are aligned with the current Fingerprint VAE baseline and will evolve as new model representations are introduced.

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

- compare configurations such as 8, 16, 32, and 64 latent dimensions;
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

## Current scope

The first controlled QM9 Fingerprint VAE baseline has been completed using a deterministic 10,000-molecule subset and non-overlapping train, validation, and test splits.

The initial baseline establishes that the pipeline can train, select a checkpoint using validation loss, and evaluate a held-out test split reproducibly.

The following research questions remain open:

- whether nearby latent vectors correspond to chemically similar molecules;
- whether molecular properties form visible patterns across latent space;
- whether reconstruction quality is meaningful according to fingerprint similarity metrics;
- how robust the results are across random seeds;
- whether alternative latent dimensions or model architectures improve the representation.

These questions require latent-vector export, scientific visualizations, additional evaluation metrics, and repeated experiments.