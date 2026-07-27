# Figures and Media Guide

Store only meaningful research figures in this directory. File names should be lowercase, descriptive, and use hyphens, for example `fingerprint-vae-training-curves-v1.png`.

## When to capture evidence

| Milestone | Save |
| --- | --- |
| Preprocessing on a larger dataset | Terminal summary and a dataset-quality table or chart. |
| First meaningful training run | Training and validation loss curves, configuration, and checkpoint metadata. |
| Latent export | PCA and UMAP plots with a caption describing the color property. |
| Explorer MVP | One clean full-window screenshot and a 10–30 second interaction recording. |
| Nearest-neighbor feature | Selected molecule plus its neighbors and similarity values. |
| Interpolation feature | A trajectory figure or short video showing the changing latent position. |

## Caption format

Every saved figure should have a nearby caption in `RESULTS.md` or `EXPERIMENTS.md` stating what the figure shows, which dataset/configuration/projection produced it, what observation it supports, and its limitation.

## Video guidance

Keep repository media lightweight. Store large recordings on a release page or video host and link them from the relevant documentation. Use video to demonstrate an interaction, not to replace a written scientific result.
