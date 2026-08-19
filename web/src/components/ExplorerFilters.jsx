const splitLabels = {
  train: 'Training',
  validation: 'Validation',
  test: 'Test',
}

export function ExplorerFilters({
  activeSplits,
  visibleCount,
  totalCount,
  onToggleSplit,
  onClearFilters,
}) {
  return (
    <section className="explorer-filters">
      <div className="filter-heading">
        <h3>Map filters</h3>

        <button type="button" onClick={onClearFilters}>
          Reset
        </button>
      </div>

      <fieldset className="split-filters">
        <legend>Dataset split</legend>

        {Object.entries(splitLabels).map(
          ([split, label]) => (
            <label key={split}>
              <input
                type="checkbox"
                checked={activeSplits.includes(split)}
                onChange={() => onToggleSplit(split)}
              />
              <span>{label}</span>
            </label>
          ),
        )}
      </fieldset>

      <p className="visible-count" aria-live="polite">
        <strong>{visibleCount.toLocaleString()}</strong> of{' '}
        {totalCount.toLocaleString()} molecules visible
      </p>
    </section>
  )
}
