const EXPECTED_SCHEMA_VERSION = 1

const DATA_ROOT = `${import.meta.env.BASE_URL}data`

function requireObject(value, label) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error(`${label} must be a JSON object.`)
  }

  return value
}

function requireSchemaVersion(payload, label) {
  requireObject(payload, label)

  if (payload.schemaVersion !== EXPECTED_SCHEMA_VERSION) {
    throw new Error(
      `${label} uses schema version ${payload.schemaVersion}; ` +
        `expected ${EXPECTED_SCHEMA_VERSION}.`,
    )
  }
}

async function fetchJson(fileName, signal) {
  const response = await fetch(`${DATA_ROOT}/${fileName}`, {
    signal,
  })

  if (!response.ok) {
    throw new Error(
      `Failed to load ${fileName}: HTTP ${response.status}.`,
    )
  }

  try {
    return await response.json()
  } catch {
    throw new Error(`${fileName} does not contain valid JSON.`)
  }
}

function validateManifest(manifest) {
  requireSchemaVersion(manifest, 'Export manifest')
  requireObject(manifest.dataset, 'Manifest dataset')
  requireObject(manifest.files, 'Manifest files')

  for (const artifactName of [
    'molecules',
    'neighbors',
    'metrics',
  ]) {
    const artifact = requireObject(
      manifest.files[artifactName],
      `Manifest ${artifactName} artifact`,
    )

    if (
      typeof artifact.fileName !== 'string' ||
      artifact.fileName.length === 0
    ) {
      throw new Error(
        `Manifest ${artifactName} artifact has no filename.`,
      )
    }
  }
}

function validateMolecules(payload, manifest) {
  requireSchemaVersion(payload, 'Molecule dataset')
  requireObject(payload.dataset, 'Molecule dataset metadata')

  if (!Array.isArray(payload.molecules)) {
    throw new Error('Molecule dataset must contain a molecule array.')
  }

  if (
    payload.molecules.length !==
    manifest.dataset.moleculeCount
  ) {
    throw new Error(
      'Molecule count does not match the export manifest.',
    )
  }
}

function validateNeighbors(payload, manifest) {
  requireSchemaVersion(payload, 'Neighbor dataset')
  requireObject(payload.queries, 'Neighbor query map')

  if (
    payload.queryCount !==
    manifest.dataset.neighborQueryCount
  ) {
    throw new Error(
      'Neighbor query count does not match the export manifest.',
    )
  }

  if (
    payload.neighborsPerQuery !==
    manifest.dataset.neighborsPerQuery
  ) {
    throw new Error(
      'Neighbors-per-query does not match the export manifest.',
    )
  }
}

function validateMetrics(payload) {
  requireSchemaVersion(payload, 'Scientific metrics')
  requireObject(
    payload.neighborAnalysis,
    'Neighbor analysis metrics',
  )
  requireObject(
    payload.reconstructionAnalysis,
    'Reconstruction metrics',
  )
  requireObject(
    payload.robustnessAnalysis,
    'Robustness metrics',
  )
}

export async function loadExplorerData({ signal } = {}) {
  const manifest = await fetchJson(
    'qm9_web_export_manifest.json',
    signal,
  )

  validateManifest(manifest)

  const [molecules, neighbors, metrics] = await Promise.all([
    fetchJson(manifest.files.molecules.fileName, signal),
    fetchJson(manifest.files.neighbors.fileName, signal),
    fetchJson(manifest.files.metrics.fileName, signal),
  ])

  validateMolecules(molecules, manifest)
  validateNeighbors(neighbors, manifest)
  validateMetrics(metrics)

  return {
    manifest,
    molecules,
    neighbors,
    metrics,
  }
}

export { EXPECTED_SCHEMA_VERSION }