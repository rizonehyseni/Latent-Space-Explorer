# Documentation Guide

This directory is the project’s technical and research record. Documentation is updated only when the related implementation or experiment exists.

## Documents

### System Understanding

| Document | Description |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System structure, components, and data flow. |
| [METHODOLOGY.md](METHODOLOGY.md) | Data representation, model design, and training approach. |

---

### Research Process

| Document | Description |
|---|---|
| [RESEARCH_QUESTIONS.md](RESEARCH_QUESTIONS.md) | Scientific questions guiding the project. |
| [DECISIONS.md](DECISIONS.md) | Design decisions, rationale, and trade-offs. |
| [LIMITATIONS.md](LIMITATIONS.md) | Current constraints and future improvements. |

---

### Experiments and Reproducibility

| Document | Description |
|---|---|
| [EXPERIMENTS.md](EXPERIMENTS.md) | Training runs, configurations, and interpretations. |
| [REPRODUCIBILITY.md](REPRODUCIBILITY.md) | Environment setup and reproduction workflow. |

---

### Reference

| Document | Description |
|---|---|
| [GLOSSARY.md](GLOSSARY.md) | Machine learning and cheminformatics terminology. |
| [FIGURES/README.md](FIGURES/README.md) | Documentation assets and visualization guidelines. |

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
