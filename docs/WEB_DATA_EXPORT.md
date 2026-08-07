# QM9 Browser Data Export

## Purpose

This export connects the completed scientific backend to the web application.

It converts aligned PCA, UMAP, molecular-property, neighbor, reconstruction, and robustness artifacts into compact JSON files that Vite can serve directly from `web/public/data/`.

## Reproduce the export

Run:

```powershell
python -m backend.export_web_data --config configs/qm9_web_export.yaml
```

Configuration:

```text
configs/qm9_web_export.yaml
```

## Generated artifacts

| File | Purpose |
|---|---|
| `qm9_molecules.json` | Molecule identity, canonical SMILES, split, PCA/UMAP coordinates, and properties |
| `qm9_neighbors.json` | Ten aligned training neighbors for each held-out test molecule |
| `qm9_metrics.json` | Compact neighbor, reconstruction, threshold-sweep, and robustness summaries |
| `qm9_web_export_manifest.json` | Schema, counts, filenames, sizes, SHA-256 checksums, and interpretation warnings |

## Molecule contract

The molecule export contains 10,000 aligned records:

- 8,000 training molecules;
- 1,000 validation molecules;
- 1,000 test molecules.

Each molecule includes:

```json
{
  "row": 0,
  "sourceIndex": 0,
  "id": "gdb_1",
  "smiles": "C",
  "split": "train",
  "coordinates": {
    "pca": [0.049301, 0.469332],
    "umap": [-0.102811, 8.483671]
  },
  "properties": {
    "molecular_weight": 16.043,
    "logp": 0.6361,
    "tpsa": 0.0,
    "ring_count": 0,
    "num_heavy_atoms": 1,
    "gap": 0.5048
  }
}
```

PCA and UMAP metadata are validated for identical molecule IDs, source indices, latent rows, SMILES, splits, and property values before export.

## Neighbor contract

The neighbor export contains 1,000 held-out test queries and ten training references per query.

Each neighbor includes:

- neighbor rank;
- aligned molecule row;
- molecule ID;
- original 16-dimensional latent distance;
- Morgan-fingerprint Tanimoto similarity.

Query molecules must belong to the test split, and neighbor references must belong to the training split.

## Metrics contract

The metrics export provides frontend-ready values for:

- latent-neighbor similarity versus random references;
- similarity by neighbor rank;
- distance/similarity correlations;
- reconstruction precision, recall, F1, and Tanimoto;
- validation-selected and reference thresholds;
- the complete threshold sweep;
- all-zero baseline results;
- robustness across seeds and latent dimensions.

## Manifest and integrity

The manifest records:

- schema version;
- dataset and split counts;
- coordinate systems;
- exported properties;
- artifact filenames and sizes;
- SHA-256 checksums;
- scientific interpretation warnings.

The export is deterministic when its source artifacts and configuration remain unchanged.

## Scientific boundaries

The frontend must communicate that:

- PCA and UMAP are two-dimensional projections;
- UMAP global distances and region sizes may be distorted;
- Tanimoto measures fingerprint overlap rather than complete chemical or biological similarity;
- the decoder reconstructs fingerprints rather than guaranteed valid molecular structures.

## Tests

Run:

```powershell
python -m unittest tests.test_web_data_export -v
```

The tests verify projection alignment, duplicate rejection, molecule and neighbor contracts, scientific metrics, numeric normalization, and manifest checksums.