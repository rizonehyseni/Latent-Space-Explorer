import { describe, expect, it } from 'vitest'
import {
  filterMolecules,
  getPropertyBounds,
} from './filterMolecules.js'

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

describe('getPropertyBounds', () => {
  it('returns the minimum and maximum finite values', () => {
    expect(
      getPropertyBounds(molecules, 'logp'),
    ).toEqual({
      minimum: -1.5,
      maximum: 2.5,
    })
  })

  it('returns zero bounds when no finite values exist', () => {
    expect(
      getPropertyBounds(
        [
          {
            properties: {
              logp: Number.NaN,
            },
          },
        ],
        'logp',
      ),
    ).toEqual({
      minimum: 0,
      maximum: 0,
    })
  })
})

describe('filterMolecules', () => {
  it('filters by dataset split and inclusive property range', () => {
    const result = filterMolecules({
      molecules,
      activeSplits: ['train', 'validation'],
      propertyName: 'logp',
      propertyMinimum: -1.5,
      propertyMaximum: 0.5,
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
      propertyName: 'logp',
      propertyMinimum: -1.5,
      propertyMaximum: 2.5,
    })

    expect(result).toEqual([])
  })

  it('excludes molecules outside the selected range', () => {
    const result = filterMolecules({
      molecules,
      activeSplits: ['train', 'validation', 'test'],
      propertyName: 'logp',
      propertyMinimum: 0,
      propertyMaximum: 1,
    })

    expect(result.map((molecule) => molecule.id)).toEqual([
      'validation-middle',
    ])
  })
})