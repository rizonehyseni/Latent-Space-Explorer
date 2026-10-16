# Glossary

| Term | Meaning |
| --- | --- |
| Atom | A chemical element within a molecule, such as carbon, oxygen, or nitrogen. |
| Canonical SMILES | A standardized text representation of a molecular structure. |
| Cheminformatics | The use of computational methods to represent, analyze, and model chemical information. |
| Decoder | The VAE component that reconstructs the input representation from a latent vector. |
| Dense neural network | A neural network built from fully connected layers. |
| Encoder | The VAE component that maps an input representation into latent distribution parameters. |
| F1 score | The harmonic mean of precision and recall; used here to score reconstructed fingerprint bits. |
| Fingerprint | A numerical representation of molecular substructures and chemical features. |
| Graph VAE | A future VAE architecture that represents molecules as atom-and-bond graphs. |
| Held-out test set | Molecules kept out of training and model selection and evaluated only once at the end. |
| HOMO–LUMO gap | The energy difference between the highest occupied and lowest unoccupied molecular orbitals, reported by QM9 in hartree (Ha). |
| KL divergence | A regularization term that measures the difference between two probability distributions. |
| Latent space | A learned compressed representation in which each molecule is represented by a continuous vector. |
| Latent vector | A specific coordinate in the learned latent space. |
| LogP | A measure related to molecular lipophilicity. |
| Morgan fingerprint | A circular molecular fingerprint generated from local atom neighborhoods. |
| PCA | Principal Component Analysis; a linear method for projecting high-dimensional data into fewer display dimensions. |
| Pearson correlation | A measure of linear association between two variables, from -1 to 1. |
| Precision | The fraction of predicted fingerprint bits that are present in the original fingerprint. |
| RDKit | An open-source cheminformatics toolkit used for molecular parsing, descriptors, and fingerprints. |
| Recall | The fraction of original fingerprint bits that the reconstruction recovers. |
| Reconstruction loss | A measure of how well a model reproduces its input representation. |
| Reparameterization trick | A VAE technique that enables gradient-based training through stochastic latent sampling. |
| SMILES | Simplified Molecular Input Line Entry System; a text format for molecular structures. |
| Spearman correlation | A rank-based measure of monotonic association between two variables, from -1 to 1. |
| Tanimoto similarity | A common similarity measure for comparing binary molecular fingerprints. |
| Threshold | The probability above which a reconstructed fingerprint bit is counted as present; selected on the validation split. |
| TPSA | Topological Polar Surface Area; a descriptor associated with molecular polarity. |
| UMAP | Uniform Manifold Approximation and Projection; a nonlinear method for visualizing high-dimensional data. |
| VAE | Variational Autoencoder; a generative model that learns a continuous latent representation. |
