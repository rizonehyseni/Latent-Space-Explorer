const splitLabels = {
  train: 'Training',
  validation: 'Validation',
  test: 'Test',
}

export function ExplorerFilters({
  activeSplits,
  propertyLabel,
  propertyBounds,
  propertyRange,
  visibleCount,
  totalCount,
  onToggleSplit,
  onChangeMinimum,
  onChangeMaximum,
  onClearFilters,
}) {
  return (
    <section className="explorer-filters">
      <div className="filter-heading">
        <h2>Map filters</h2>

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

      <div className="property-range-filter">
        <p>{propertyLabel} range</p>

        <div className="range-inputs">
          <label>
            <span>Minimum</span>
            <input
              type="number"
              step="any"
              min={propertyBounds.minimum}
              max={propertyBounds.maximum}
              value={propertyRange.minimum}
              onChange={(event) => {
                if (Number.isFinite(event.target.valueAsNumber)) {
                  onChangeMinimum(
                    event.target.valueAsNumber,
                  )
                }
              }}
            />
          </label>

          <label>
            <span>Maximum</span>
            <input
              type="number"
              step="any"
              min={propertyBounds.minimum}
              max={propertyBounds.maximum}
              value={propertyRange.maximum}
              onChange={(event) => {
                if (Number.isFinite(event.target.valueAsNumber)) {
                  onChangeMaximum(
                    event.target.valueAsNumber,
                  )
                }
              }}
            />
          </label>
        </div>

        <p className="available-range">
          Available: {propertyBounds.minimum.toFixed(3)} to{' '}
          {propertyBounds.maximum.toFixed(3)}
        </p>
      </div>

      <p className="visible-count" aria-live="polite">
        <strong>{visibleCount.toLocaleString()}</strong> of{' '}
        {totalCount.toLocaleString()} molecules visible
      </p>
    </section>
  )
}