 <h1>Latent Space Explorer: Generative VAE framework for molecular topology</h1>

<div align="justify>

Latent Space Explorer is a generative VAE framework designed to navigate the hidden dimensions of chemical space. By mapping complex latent representations into structural reality, the project enables researchers to see and explore what was previously hidden in the data. The project aims to bridge the gap between high-dimensional latent space representation and intuitive 3D molecular topology.

### System Understanding

| Document | Description |
|---|---|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System structure, components, and data flow. |
| [METHODOLOGY.md](docs/METHODOLOGY.md) | Data representation, model design, and training approach. |

---

### Research Process

| Document | Description |
|---|---|
| [RESEARCH_QUESTIONS.md](docs/RESEARCH_QUESTIONS.md) | Scientific questions guiding the project. |
| [DECISIONS.md](docs/DECISIONS.md) | Design decisions, rationale, and trade-offs. |
| [LIMITATIONS.md](docs/LIMITATIONS.md) | Current constraints and future improvements. |

---

### Experiments and Reproducibility

| Document | Description |
|---|---|
| [EXPERIMENTS.md](docs/EXPERIMENTS.md) | Training runs, configurations, and interpretations. |
| [REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md) | Environment setup and reproduction workflow. |

---

### Reference

| Document | Description |
|---|---|
| [GLOSSARY.md](docs/GLOSSARY.md) | Machine learning and cheminformatics terminology. |
| [FIGURES/README.md](docs/FIGURES/README.md) | Documentation assets and visualization guidelines. |

## Documentation rule for each completed feature

When a feature branch delivers working behavior, update only the documents affected by that behavior:

1. Update `ARCHITECTURE.md` if the system flow, data contract, or component responsibilities changed.
2. Update `PROJECT_STATUS.md` when a milestone is completed or the next milestone changes.
3. Add an entry to `EXPERIMENTS.md` when a training run produces a result worth retaining.
4. Update `DECISIONS.md` if a significant technical choice was made.
5. Update `LIMITATIONS.md` if a limitation is removed or newly identified.
6. Save a figure or short recording only when it demonstrates a meaningful result or interaction.

Do not document planned functionality as implemented functionality.

## Reproducibility record

Every retained experiment should identify:

- dataset source and molecule count;
- preprocessing settings;
- experiment configuration path;
- random seed;
- Git commit;
- training, validation, and test metrics where available;
- interpretation and limitations.

</div>
