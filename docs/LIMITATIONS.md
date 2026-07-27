# Current Limitations

This document describes the current technical and scientific limitations of the project. These limitations are recorded explicitly so that results are interpreted responsibly and future work can address them systematically.

## Dataset scale

The tracked development dataset contains only three molecules.

This dataset is useful for:

- verifying CSV ingestion;
- validating RDKit preprocessing;
- confirming fingerprint generation;
- testing training and checkpoint creation;
- verifying the train/validation workflow.

It is not suitable for:

- scientific model evaluation;
- hyperparameter selection;
- cluster analysis;
- molecular-property conclusions;
- generalization claims.

## Validation sample size

The current validation configuration reserves 20% of the three-molecule development dataset.

This produces:

- 2 training molecules;
- 1 validation molecule.

The validation workflow is technically correct, but one validation molecule cannot provide a stable or statistically meaningful measure of model quality.

## No held-out test set

The current workflow includes training and validation data only.

A future larger dataset must contain:

- training data for model optimization;
- validation data for model selection;
- test data for final unbiased evaluation.

## Fingerprint reconstruction is not molecular generation

The current model reconstructs Morgan fingerprints.

Therefore:

- latent exploration is possible;
- fingerprint reconstruction is measurable;
- similarity analysis is possible.

However:

- latent vectors do not decode directly into valid SMILES;
- generated molecular graphs are not available;
- chemical validity cannot yet be guaranteed;
- interpolation does not yet produce chemically valid molecular structures.

## Dense VAE representation limits

The current VAE uses fixed-size fingerprint vectors and dense neural-network layers.

This is appropriate for the baseline, but it does not explicitly model:

- atoms;
- bond types;
- graph topology;
- stereochemistry;
- molecular conformations;
- three-dimensional geometry.

A future Graph VAE or another graph-based representation would address some of these limitations.

## No latent-space export yet

The project does not yet export encoded latent vectors and display coordinates for browser visualization.

As a result, the current React/Vite frontend cannot yet display:

- molecular point clouds;
- PCA or UMAP projections;
- nearest-neighbor regions;
- property-colored latent spaces;
- interpolation trajectories.

## No molecular property prediction model

The project calculates observed molecular descriptors during preprocessing, but it does not yet predict properties from latent vectors.

Therefore, interpolated or generated latent points cannot yet be assigned reliable property estimates.

## No chemical-validity evaluation

The project does not currently evaluate:

- valid SMILES rate;
- synthetic accessibility;
- drug-likeness;
- molecular novelty;
- molecular diversity;
- property constraint satisfaction.

These metrics become relevant after a model can generate molecular structures rather than only fingerprint reconstructions.