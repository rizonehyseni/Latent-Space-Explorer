import { useState } from 'react'
import { useExplorerData } from './hooks/useExplorerData.js'
import './App.css'
import { LatentScatterPlot } from './components/LatentScatterPlot.jsx'
import { MoleculeInspector } from './components/MoleculeInspector.jsx'

const numberFormatter = new Intl.NumberFormat('en-US')

const propertyLabels = {
  molecular_weight: 'Molecular weight',
  logp: 'LogP',
  tpsa: 'TPSA',
  ring_count: 'Ring count',
  num_heavy_atoms: 'Heavy atoms',
  gap: 'HOMO–LUMO gap',
}

function formatMetric(value) {
  return Number(value).toFixed(3)
}

function LoadingState() {
  return (
    <main className="state-page">
      <section className="state-message" aria-live="polite">
        <div className="loading-indicator" aria-hidden="true" />
        <p className="eyebrow">Preparing explorer</p>
        <h1>Loading QM9 latent-space data</h1>
        <p>
          Aligning molecular projections, properties, neighbors,
          and scientific metrics.
        </p>
      </section>
    </main>
  )
}

function ErrorState({ error, retry }) {
  return (
    <main className="state-page">
      <section className="state-message error-message" role="alert">
        <p className="eyebrow">Data loading failed</p>
        <h1>Unable to open the dataset</h1>
        <p>{error.message}</p>
        <button type="button" onClick={retry}>
          Retry
        </button>
      </section>
    </main>
  )
}

function ExplorerDashboard({ data }) {
  const [projection, setProjection] = useState('umap')
  const [colorProperty, setColorProperty] = useState('gap')
  const [selectedMolecule, setSelectedMolecule] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchMessage, setSearchMessage] = useState('') 
  const { manifest, molecules,neighbors, metrics } = data
  const { dataset } = manifest
  const neighborMetrics = metrics.neighborAnalysis
  const reconstructionMetrics = metrics.reconstructionAnalysis

  function handleMoleculeSearch(event) {
  event.preventDefault()

  const normalizedQuery = searchQuery.trim().toLowerCase()

  if (!normalizedQuery) {
    setSearchMessage('Enter a molecule ID.')
    return
  }

  const matchingMolecule = molecules.molecules.find(
    (molecule) =>
      molecule.id.toLowerCase() === normalizedQuery,
  )

  if (!matchingMolecule) {
    setSearchMessage(
      `No molecule found with ID "${searchQuery.trim()}".`,
    )
    return
  }

  setSelectedMolecule(matchingMolecule)
  setSearchQuery(matchingMolecule.id)
  setSearchMessage(`Selected ${matchingMolecule.id}.`)
}
  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-symbol" aria-hidden="true">
            LS
          </span>

          <div>
            <h1>Latent Space Explorer</h1>
          </div>
        </div>

        <nav className="projection-navigation" aria-label="Projection">
          {dataset.coordinateSystems.map((coordinateSystem) => (
            <button
              className={
                projection === coordinateSystem ? 'active' : ''
              }
              key={coordinateSystem}
              type="button"
              onClick={() => setProjection(coordinateSystem)}
            >
              {coordinateSystem.toUpperCase()}
            </button>
          ))}
        </nav>

      </header>

      <div className="explorer-layout">
        <aside className="context-panel">
          <p className="eyebrow">Molecular map</p>


          <p className="introduction">
            Each point represents one molecule encoded by the
            fingerprint variational autoencoder. Nearby points may
            share structural characteristics.
          </p>


          <div className="map-controls">
            <label htmlFor="color-property">
              Color molecules by
            </label>

            <select
              id="color-property"
              value={colorProperty}
              onChange={(event) =>
                setColorProperty(event.target.value)
              }
            >
              {dataset.properties.map((property) => (
                <option key={property} value={property}>
                  {propertyLabels[property] ?? property}
                </option>
              ))}
            </select>

            <label htmlFor="molecule-search">
              Find a molecule
            </label>

            <form
  className="search-control"
  onSubmit={handleMoleculeSearch}
>
  <input
    id="molecule-search"
    type="search"
    value={searchQuery}
    placeholder="e.g. gdb_1001"
    aria-describedby="search-message"
    onChange={(event) => {
      setSearchQuery(event.target.value)
      setSearchMessage('')
    }}
  />

  <button type="submit">Find</button>
</form>

<p
  className="search-message"
  id="search-message"
  aria-live="polite"
>
  {searchMessage}
</p>
          </div>

          <details className="interpretation-note">
            <summary>Interpretation guidance</summary>
            <ul>
              {manifest.scientificWarnings.map((warning) => (
                <li key={warning}>{warning}</li>
              ))}
            </ul>
          </details>
        </aside>

        <section className="map-workspace">
          <div className="map-heading">
            <div>
              <p className="eyebrow">
                Learned representation
              </p>
              <h2>{projection.toUpperCase()} projection</h2>
            </div>

            <div className="map-heading-meta">
              <span>
                Color: {propertyLabels[colorProperty]}
              </span>
              <span>
                {numberFormatter.format(
                  molecules.molecules.length,
                )}{' '}
                points
              </span>
            </div>
          </div>

<div className="plot-layout">
  <LatentScatterPlot
    molecules={molecules.molecules}
    projection={projection}
    colorProperty={colorProperty}
    selectedMolecule={selectedMolecule}
    onSelectMolecule={setSelectedMolecule}
  />
</div>

<MoleculeInspector
  selectedMolecule={selectedMolecule}
  projection={projection}
  molecules={molecules.molecules}
  neighbors={neighbors}
  onSelectMolecule={setSelectedMolecule}
/>
         

          <div className="evidence-strip">
            <div>
              <span>Neighbor Tanimoto</span>
              <strong>
                {formatMetric(
                  neighborMetrics.meanNeighborTanimoto,
                )}
              </strong>
            </div>

            <div>
              <span>Random baseline</span>
              <strong>
                {formatMetric(
                  neighborMetrics.meanRandomTanimoto,
                )}
              </strong>
            </div>

            <div>
              <span>Reconstruction F1</span>
              <strong>
                {formatMetric(
                  reconstructionMetrics.metrics.f1Score,
                )}
              </strong>
            </div>

            <div>
              <span>Reconstruction Tanimoto</span>
              <strong>
                {formatMetric(
                  reconstructionMetrics.metrics.meanTanimoto,
                )}
              </strong>
            </div>
          </div>
        </section>
      </div>

      <footer className="site-footer">
        <span>Latent Space Explorer</span>
        <span>
          Schema v{manifest.schemaVersion} · scientific prototype
        </span>
      </footer>
    </main>
  )
}

function App() {
  const { status, data, error, retry } = useExplorerData()

  if (status === 'loading') {
    return <LoadingState />
  }

  if (status === 'error') {
    return <ErrorState error={error} retry={retry} />
  }

  return <ExplorerDashboard data={data} />
}

export default App