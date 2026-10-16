import { useMemo, useSyncExternalStore } from 'react'
import createPlotlyComponent from 'react-plotly.js/factory'
import Plotly from 'plotly.js-gl2d-dist-min'

const Plot = createPlotlyComponent(Plotly)

// Matches the mobile breakpoint used in App.css.
const narrowScreenQuery = '(max-width: 600px)'

function subscribeToScreenWidth(onChange) {
  const mediaQuery = window.matchMedia(narrowScreenQuery)
  mediaQuery.addEventListener('change', onChange)
  return () => mediaQuery.removeEventListener('change', onChange)
}

function getIsNarrowScreen() {
  return window.matchMedia(narrowScreenQuery).matches
}

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
  const isNarrowScreen = useSyncExternalStore(
    subscribeToScreenWidth,
    getIsNarrowScreen,
  )
  const fontSize = isNarrowScreen ? 12 : 14

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
              side: isNarrowScreen ? 'top' : 'right',
              font: {
                size: fontSize,
                color: '#d8dee9',
              },
            },
            // On phones a horizontal bar above the plot leaves the
            // full width for the points.
            ...(isNarrowScreen
              ? {
                  orientation: 'h',
                  x: 0.5,
                  xanchor: 'center',
                  y: 1.02,
                  yanchor: 'bottom',
                  thickness: 10,
                  len: 1,
                }
              : {
                  thickness: 12,
                  len: 0.75,
                }),
            outlinewidth: 0,
            tickfont: {
              size: fontSize,
              color: '#9ba8b5',
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
    isNarrowScreen,
    fontSize,
  ])

  const layout = useMemo(
    () => ({
      autosize: true,
      dragmode: 'pan',
      hovermode: 'closest',
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      // Plotly reads margins from l, r, t, and b only.
      margin: isNarrowScreen
        ? {
            t: 64,
            r: 16,
            b: 48,
            l: 44,
          }
        : {
            t: 20,
            r: 100,
            b: 60,
            l: 70,
          },
      font: {
        family: 'JetBrains Mono, Cascadia Code, Consolas, monospace',
        size: fontSize,
        color: '#9ba8b5',
      },
      xaxis: {
        title: { text: `${projection.toUpperCase()} 1` },
        gridcolor: '#27313b',
        zerolinecolor: '#3a4652',
        linecolor: '#59636e',
        tickfont: {
          size: fontSize,
        },
      },
      yaxis: {
        title: { text: `${projection.toUpperCase()} 2` },
        gridcolor: '#27313b',
        zerolinecolor: '#3a4652',
        linecolor: '#59636e',
        tickfont: {
          size: fontSize,
        },
      },
      uirevision: `${projection}-${colorProperty}`,
    }),
    [projection, colorProperty, isNarrowScreen, fontSize],
  )

  function handlePointClick(event) {
    const point = event.points[0]
    const moleculeIndex = point.customdata[3]

    onSelectMolecule(molecules[moleculeIndex])
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