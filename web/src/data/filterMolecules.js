export function filterMolecules({
  molecules,
  activeSplits,
}) {
  const includedSplits = new Set(activeSplits)

  return molecules.filter((molecule) =>
    includedSplits.has(molecule.split),
  )
}
