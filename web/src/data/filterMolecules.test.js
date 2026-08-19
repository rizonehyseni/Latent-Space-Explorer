import { describe, expect, it } from 'vitest'
import { filterMolecules } from './filterMolecules.js'

const molecules = [
  {
    id: 'train-low',
    split: 'train',
    properties: {
      logp: -1.5,
    },
  },
  {
    id: 'validation-middle',
    split: 'validation',
    properties: {
      logp: 0.5,
    },
  },
  {
    id: 'test-high',
    split: 'test',
    properties: {
      logp: 2.5,
    },
  },
]

describe('filterMolecules', () => {
  it('filters molecules by dataset split', () => {
    const result = filterMolecules({
      molecules,
      activeSplits: ['train', 'validation'],
    })

    expect(result.map((molecule) => molecule.id)).toEqual([
      'train-low',
      'validation-middle',
    ])
  })

  it('returns no molecules when every split is disabled', () => {
    const result = filterMolecules({
      molecules,
      activeSplits: [],
    })

    expect(result).toEqual([])
  })

  it('returns every molecule when all splits are enabled', () => {
    const result = filterMolecules({
      molecules,
      activeSplits: ['train', 'validation', 'test'],
    })

    expect(result.map((molecule) => molecule.id)).toEqual([
      'train-low',
      'validation-middle',
      'test-high',
    ])
  })
})
