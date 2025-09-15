import React from 'react'
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js'
import { Radar } from 'react-chartjs-2'

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
)

function RadarChart({ comparison, country1Name, country2Name }) {
  if (!comparison || !comparison.comparison_metrics) {
    return (
      <div className="chart-container">
        <div className="text-center py-8">
          <p className="text-dark-400">No comparison data available</p>
        </div>
      </div>
    )
  }

  const metrics = comparison.comparison_metrics
  const labels = Object.keys(metrics).map(key => {
    const labelMap = {
      'population': 'Population',
      'area': 'Area',
      'gdp': 'GDP',
      'gdp_per_capita': 'GDP per Capita',
      'hdi': 'HDI',
      'life_expectancy': 'Life Expectancy',
      'internet_penetration': 'Internet Penetration'
    }
    return labelMap[key] || key
  })

  // Normalize data to 0-100 scale for radar chart
  const normalizeValue = (value, metric) => {
    if (!value || value === 0) return 0
    
    // Define max values for normalization (these would ideally come from global max values)
    const maxValues = {
      'population': 1500000000, // 1.5B
      'area': 17000000, // 17M km²
      'gdp': 25000000000000, // 25T USD
      'gdp_per_capita': 100000, // 100K USD
      'hdi': 1.0,
      'life_expectancy': 85,
      'internet_penetration': 100
    }
    
    const max = maxValues[metric] || 100
    return Math.min((value / max) * 100, 100)
  }

  const country1Data = labels.map((label, index) => {
    const metricKey = Object.keys(metrics)[index]
    return normalizeValue(metrics[metricKey].country1, metricKey)
  })

  const country2Data = labels.map((label, index) => {
    const metricKey = Object.keys(metrics)[index]
    return normalizeValue(metrics[metricKey].country2, metricKey)
  })

  const data = {
    labels,
    datasets: [
      {
        label: country1Name,
        data: country1Data,
        backgroundColor: 'rgba(239, 68, 68, 0.2)',
        borderColor: 'rgba(239, 68, 68, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(239, 68, 68, 1)',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 6,
      },
      {
        label: country2Name,
        data: country2Data,
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(59, 130, 246, 1)',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 6,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#e2e8f0',
          font: {
            family: 'Inter',
            size: 12,
          },
          usePointStyle: true,
          pointStyle: 'circle',
        },
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        titleColor: '#f1f5f9',
        bodyColor: '#cbd5e1',
        borderColor: '#334155',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          label: function(context) {
            const metricKey = Object.keys(metrics)[context.dataIndex]
            const originalValue = metrics[metricKey][context.datasetIndex === 0 ? 'country1' : 'country2']
            const label = context.dataset.label
            
            // Format the original value for display
            let formattedValue = originalValue
            if (metricKey === 'population') {
              formattedValue = (originalValue / 1000000).toFixed(1) + 'M'
            } else if (metricKey === 'area') {
              formattedValue = originalValue.toLocaleString() + ' km²'
            } else if (metricKey === 'gdp') {
              formattedValue = '$' + (originalValue / 1000000000).toFixed(1) + 'B'
            } else if (metricKey === 'gdp_per_capita') {
              formattedValue = '$' + originalValue.toLocaleString()
            } else if (metricKey === 'hdi') {
              formattedValue = originalValue.toFixed(3)
            } else if (metricKey === 'life_expectancy') {
              formattedValue = originalValue.toFixed(1) + ' years'
            } else if (metricKey === 'internet_penetration') {
              formattedValue = originalValue.toFixed(1) + '%'
            }
            
            return `${label}: ${formattedValue}`
          }
        }
      },
    },
    scales: {
      r: {
        beginAtZero: true,
        max: 100,
        min: 0,
        ticks: {
          color: '#64748b',
          font: {
            family: 'Inter',
            size: 10,
          },
          stepSize: 20,
          callback: function(value) {
            return value + '%'
          }
        },
        grid: {
          color: '#334155',
        },
        angleLines: {
          color: '#334155',
        },
        pointLabels: {
          color: '#e2e8f0',
          font: {
            family: 'Inter',
            size: 11,
            weight: '500',
          },
        },
      },
    },
    elements: {
      line: {
        tension: 0.1,
      },
    },
  }

  return (
    <div className="chart-container">
      <div className="mb-6">
        <h3 className="text-xl font-semibold text-white mb-2">Multi-Dimensional Comparison</h3>
        <p className="text-dark-400 text-sm">
          Compare countries across key indicators (normalized to 0-100 scale)
        </p>
      </div>
      
      <div className="h-96">
        <Radar data={data} options={options} />
      </div>
      
      <div className="mt-4 p-4 bg-dark-700 rounded-lg">
        <p className="text-dark-300 text-xs">
          <strong>Note:</strong> Values are normalized to a 0-100 scale for comparison. 
          Hover over data points to see actual values.
        </p>
      </div>
    </div>
  )
}

export default RadarChart
