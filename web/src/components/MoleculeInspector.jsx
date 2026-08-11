import { useMemo } from 'react'

const propertyDefinitions = [
  {
    key: 'molecular_weight',
    label: 'Molecular weight',
    unit: 'g/mol',
  },
  {
    key: 'logp',
    label: 'LogP',
    unit: '',
  },
  {
    key: 'tpsa',
    label: 'TPSA',
    unit: 'Å²',
  },
  {
    key: 'ring_count',
    label: 'Ring count',
    unit: '',
  },
  {
    key: 'num_heavy_atoms',
    label: 'Heavy atoms',
    unit: '',
  },
  {
    key: 'gap',
    label: 'HOMO–LUMO gap',
    unit: 'Ha',
  },
]

function formatValue(value) {
  if (!Number.isFinite(value)) {
    return '—'
  }

  return Number.isInteger(value)
    ? value.toString()
    : value.toFixed(3)
}

export function MoleculeInspector({
  selectedMolecule,
  projection,
  molecules,
  neighbors,
  onSelectMolecule,
}) {
  const moleculeById = useMemo(
    () =>
      new Map(
        molecules.map((molecule) => [
          molecule.id,
          molecule,
        ]),
      ),
    [molecules],
  )

  if (!selectedMolecule) {
    return (
      <section className="molecule-inspector empty-inspector">
        <h2>Molecule inspector</h2>
        <p>
          Select a point from the molecular map or search for a
          molecule ID to inspect its properties and neighbors.
        </p>
      </section>
    )
  }

  const coordinates =
    selectedMolecule.coordinates[projection]

  const neighborQuery =
    neighbors.queries[selectedMolecule.id]

  return (
    <section className="molecule-inspector">
      <div className="inspector-heading">
        <div>
          <h2>{selectedMolecule.id}</h2>
          <p>
            {selectedMolecule.split} dataset split
          </p>
        </div>

        <span>{projection.toUpperCase()}</span>
      </div>

      <div className="smiles-value">
        <span>SMILES</span>
        <code>{selectedMolecule.smiles}</code>
      </div>

      <dl className="coordinate-values">
        <div>
          <dt>{projection.toUpperCase()} X</dt>
          <dd>{coordinates[0].toFixed(3)}</dd>
        </div>

        <div>
          <dt>{projection.toUpperCase()} Y</dt>
          <dd>{coordinates[1].toFixed(3)}</dd>
        </div>
      </dl>

      <div className="property-section">
        <h3>Molecular properties</h3>

        <dl className="property-values">
          {propertyDefinitions.map(
            ({ key, label, unit }) => (
              <div key={key}>
                <dt>{label}</dt>
                <dd>
                  {formatValue(
                    selectedMolecule.properties[key],
                  )}
                  {unit && <small> {unit}</small>}
                </dd>
              </div>
            ),
          )}
        </dl>
      </div>

      <div className="neighbor-section">
        <h3>Nearest latent neighbors</h3>

        {!neighborQuery && (
          <p className="neighbor-message">
            Neighbor results are available for the 1,000 held-out
            test queries included in the scientific evaluation.
          </p>
        )}

        {neighborQuery && (
          <div className="neighbor-table-wrapper">
            <table className="neighbor-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Molecule</th>
                  <th>Distance</th>
                  <th>Tanimoto</th>
                </tr>
              </thead>

              <tbody>
                {neighborQuery.neighbors.map((neighbor) => {
                  const neighborMolecule =
                    moleculeById.get(neighbor.id)

                  return (
                    <tr key={neighbor.id}>
                      <td>{neighbor.rank}</td>
                      <td>
                        <button
                          type="button"
                          disabled={!neighborMolecule}
                          onClick={() =>
                            onSelectMolecule(
                              neighborMolecule,
                            )
                          }
                        >
                          {neighbor.id}
                        </button>
                      </td>
                      <td>
                        {neighbor.latentDistance.toFixed(3)}
                      </td>
                      <td>
                        {neighbor.tanimoto.toFixed(3)}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  )
}