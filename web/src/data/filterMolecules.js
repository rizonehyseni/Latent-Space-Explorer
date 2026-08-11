export function getPropertyBounds(molecules, propertyName) {
  let minimum = Infinity
  let maximum = -Infinity

  for (const molecule of molecules) {
    const value = molecule.properties[propertyName]

    if (!Number.isFinite(value)) {
      continue
    }

    minimum = Math.min(minimum, value)
    maximum = Math.max(maximum, value)
  }

  if (!Number.isFinite(minimum) || !Number.isFinite(maximum)) {
    return {
      minimum: 0,
      maximum: 0,
    }
  }

  return {
    minimum,
    maximum,
  }
}

export function filterMolecules({
  molecules,
  activeSplits,
  propertyName,
  propertyMinimum,
  propertyMaximum,
}) {
  const includedSplits = new Set(activeSplits)

  return molecules.filter((molecule) => {
    if (!includedSplits.has(molecule.split)) {
      return false
    }

    const propertyValue =
      molecule.properties[propertyName]

    return (
      Number.isFinite(propertyValue) &&
      propertyValue >= propertyMinimum &&
      propertyValue <= propertyMaximum
    )
  })
}