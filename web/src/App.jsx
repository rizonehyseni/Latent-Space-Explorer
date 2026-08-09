import { useExplorerData } from './hooks/useExplorerData.js'
import './App.css'

const numberFormatter = new Intl.NumberFormat('en-US')

function formatMetric(value) {
  return Number(value).toFixed(4)
}

function LoadingState() {
  return (
    <main className="state-page">
      <section className="state-card" aria-live="polite">
        <div className="loading-indicator" aria-hidden="true" />
        <p className="eyebrow">Preparing the explorer</p>
        <h1>Loading aligned QM9 data</h1>
        <p>
          Reading molecule coordinates, molecular properties,
          neighbors, and scientific metrics.
        </p>
      </section>
    </main>
  )
}

function ErrorState({ error, retry }) {
  return (
    <main className="state-page">
      <section className="state-card error-card" role="alert">
        <p className="eyebrow">Data loading failed</p>
        <h1>Unable to open the latent-space dataset</h1>
        <p>{error.message}</p>
        <button type="button" onClick={retry}>
          Retry
        </button>
      </section>
    </main>
  )
}

function MetricCard({ label, value, description }) {
  return (
    <article className="metric-card">
      <p>{label}</p>
      <strong>{value}</strong>
      <span>{description}</span>
    </article>
  )
}

function ExplorerOverview({ data }) {
  const { manifest, molecules, metrics } = data
  const { dataset } = manifest
  const splitCounts = dataset.splitCounts
  const neighborMetrics = metrics.neighborAnalysis
  const reconstructionMetrics =
    metrics.reconstructionAnalysis
  const robustnessMetrics = metrics.robustnessAnalysis

  return (
    <div className="app-shell">
      <header className="site-header">
        <div>
          <p className="eyebrow">Molecular representation analysis</p>
          <h1>Latent Space Explorer</h1>
          <p className="subtitle">
            Explore QM9 molecular fingerprints, latent projections,
            nearest neighbors, and model evidence.
          </p>
        </div>

        <div className="dataset-badge">
          <span>Dataset</span>
          <strong>{dataset.name}</strong>
          <small>
            {numberFormatter.format(dataset.moleculeCount)} molecules
          </small>
        </div>
      </header>

      <main>
        <section className="summary-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Data connection verified</p>
              <h2>Browser dataset overview</h2>
            </div>
            <span className="schema-badge">
              Schema v{manifest.schemaVersion}
            </span>
          </div>

          <div className="split-summary">
            <MetricCard
              label="Training"
              value={numberFormatter.format(splitCounts.train)}
              description="Model-fitting molecules"
            />
            <MetricCard
              label="Validation"
              value={numberFormatter.format(
                splitCounts.validation,
              )}
              description="Checkpoint and threshold selection"
            />
            <MetricCard
              label="Test"
              value={numberFormatter.format(splitCounts.test)}
              description="Held-out evaluation molecules"
            />
            <MetricCard
              label="Loaded records"
              value={numberFormatter.format(
                molecules.molecules.length,
              )}
              description="PCA and UMAP rows aligned"
            />
          </div>
        </section>

        <section className="summary-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Scientific evidence</p>
              <h2>Current quantitative results</h2>
            </div>
          </div>

          <div className="result-grid">
            <MetricCard
              label="Neighbor Tanimoto"
              value={formatMetric(
                neighborMetrics.meanNeighborTanimoto,
              )}
              description="Mean latent-neighbor similarity"
            />
            <MetricCard
              label="Random baseline"
              value={formatMetric(
                neighborMetrics.meanRandomTanimoto,
              )}
              description="Mean random-reference similarity"
            />
            <MetricCard
              label="Reconstruction F1"
              value={formatMetric(
                reconstructionMetrics.metrics.f1Score,
              )}
              description="Validation-selected threshold"
            />
            <MetricCard
              label="Reconstruction Tanimoto"
              value={formatMetric(
                reconstructionMetrics.metrics.meanTanimoto,
              )}
              description="Mean held-out similarity"
            />
            <MetricCard
              label="Robustness runs"
              value={robustnessMetrics.runCount}
              description="Three seeds × three dimensions"
            />
          </div>
        </section>

        <section className="summary-section warning-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Interpretation boundaries</p>
              <h2>Read the map carefully</h2>
            </div>
          </div>

          <ul>
            {manifest.scientificWarnings.map((warning) => (
              <li key={warning}>{warning}</li>
            ))}
          </ul>
        </section>
      </main>
    </div>
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

  return <ExplorerOverview data={data} />
}

export default App