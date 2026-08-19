import { useMemo } from 'react'
import createPlotlyComponent from 'react-plotly.js/factory'
import Plotly from 'plotly.js-dist-min'

const Plot = createPlotlyComponent(Plotly)

const propertyLabels = {
  molecular_weight: 'Molecular weight',
  logp: 'LogP',
  tpsa: 'TPSA',
  ring_count: 'Ring count',
  num_heavy_atoms: 'Heavy atoms',
  gap: 'HOMO–LUMO gap',
}

export function LatentScatterPlot({
  molecules,
  projection,
  colorProperty,
  selectedMolecule,
  onSelectMolecule,
}) {
  const plotData = useMemo(() => {
    const x = []
    const y = []
    const colors = []
    const customData = []

    molecules.forEach((molecule, index) => {
      const coordinates = molecule.coordinates[projection]

      x.push(coordinates[0])
      y.push(coordinates[1])
      colors.push(molecule.properties[colorProperty])
      customData.push([
        molecule.id,
        molecule.split,
        molecule.smiles,
        index,
      ])
    })

    const selectedIndex = selectedMolecule
      ? molecules.findIndex(
          (molecule) => molecule.id === selectedMolecule.id,
        )
      : -1

    return [
      {
        type: 'scattergl',
        mode: 'markers',
        x,
        y,
        customdata: customData,
        selectedpoints:
          selectedIndex >= 0 ? [selectedIndex] : undefined,
        marker: {
          size: 5,
          opacity: 0.72,
          color: colors,
          colorscale: [
  [0, '#8870ff'],
  [0.5, '#eff0eb'],
  [1, '#d31111'],
],
          showscale: true,
          colorbar: {
            title: {
              text:
                propertyLabels[colorProperty] ?? colorProperty,
              side: 'right',
            },
            thickness: 12,
            len: 0.75,
            outlinewidth: 0,
            tickfont: {
              size: 14,
              color: '#9ba8b5',
            },
            titlefont: {
              size: 14,
              color: '#d8dee9',
            },
          },
        },
        selected: {
          marker: {
            size: 10,
            opacity: 1,
            color: '#ffffff',
          },
        },
        unselected: {
          marker: {
            opacity: 0.55,
          },
        },
        hovertemplate:
          '<b>%{customdata[0]}</b><br>' +
          'Split: %{customdata[1]}<br>' +
          `${propertyLabels[colorProperty] ?? colorProperty}: ` +
          '%{marker.color:.4f}<br>' +
          'SMILES: %{customdata[2]}' +
          '<extra></extra>',
      },
    ]
  }, [
    molecules,
    projection,
    colorProperty,
    selectedMolecule,
  ])

  const layout = useMemo(
    () => ({
      autosize: true,
      dragmode: 'pan',
      hovermode: 'closest',
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      margin: {
        top: 20,
        right: 100,
        bottom: 60,
        left: 70,
      },
      font: {
        family: 'JetBrains Mono, Cascadia Code, Consolas, monospace',
        size: 14,
        color: '#9ba8b5',
      },
      xaxis: {
        title: `${projection.toUpperCase()} 1`,
        gridcolor: '#27313b',
        zerolinecolor: '#3a4652',
        linecolor: '#59636e',
        tickfont: {
          size: 14,
        },
      },
      yaxis: {
        title: `${projection.toUpperCase()} 2`,
        gridcolor: '#27313b',
        zerolinecolor: '#3a4652',
        linecolor: '#59636e',
        tickfont: {
          size: 14,
        },
      },
      uirevision: `${projection}-${colorProperty}`,
    }),
    [projection, colorProperty],
  )

function handlePointClick(event) {
  const point = event?.points?.[0]
  const moleculeIndex = point?.customdata?.[3]

  if (!Number.isInteger(moleculeIndex)) {
    return
  }

  const molecule = molecules[moleculeIndex]

  if (molecule) {
    onSelectMolecule(molecule)
  }
}

  return (
    <Plot
      className="latent-scatter-plot"
      data={plotData}
      layout={layout}
      config={{
        responsive: true,
        displaylogo: false,
        scrollZoom: true,
        toImageButtonOptions: {
    format: 'png',
    filename: `qm9-${projection}-${colorProperty}`,
    width: 1200,
    height: 800,
    scale: 2,
  },
      }}
      useResizeHandler
      onClick={handlePointClick}
      style={{
        width: '100%',
        height: '100%',
      }}
    />
  )
}