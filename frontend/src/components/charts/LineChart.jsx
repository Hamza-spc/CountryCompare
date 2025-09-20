import React from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

function LineChart({ historicalData, country1Name, country2Name, indicator }) {
  if (!historicalData || !historicalData.country1 || !historicalData.country2) {
    return (
      <div className="chart-container">
        <div className="text-center py-8">
          <p className="text-dark-400">No historical data available</p>
        </div>
      </div>
    )
  }

  const indicatorLabels = {
    'NY.GDP.MKTP.CD': 'GDP (Current US$)',
    'NY.GDP.PCAP.CD': 'GDP per Capita (Current US$)',
    'SP.DYN.LE00.IN': 'Life Expectancy at Birth',
    'IT.NET.USER.ZS': 'Internet Users (% of Population)',
    'SP.POP.TOTL': 'Population, Total'
  }

  const formatValue = (value, indicator) => {
    if (indicator === 'NY.GDP.MKTP.CD') {
      return (value / 1000000000).toFixed(1) + 'B'
    } else if (indicator === 'NY.GDP.PCAP.CD') {
      return '$' + value.toLocaleString()
    } else if (indicator === 'SP.DYN.LE00.IN') {
      return value.toFixed(1) + ' years'
    } else if (indicator === 'IT.NET.USER.ZS') {
      return value.toFixed(1) + '%'
    } else if (indicator === 'SP.POP.TOTL') {
      return (value / 1000000).toFixed(1) + 'M'
    }
    return value.toLocaleString()
  }

  const data1 = historicalData.country1.data || []
  const data2 = historicalData.country2.data || []

  // Get all unique years and sort them
  const allYears = [...new Set([...data1.map(d => d.year), ...data2.map(d => d.year)])]
    .sort((a, b) => a - b)

  // Create datasets with consistent years
  const country1Values = allYears.map(year => {
    const dataPoint = data1.find(d => d.year === year)
    return dataPoint ? dataPoint.value : null
  })

  const country2Values = allYears.map(year => {
    const dataPoint = data2.find(d => d.year === year)
    return dataPoint ? dataPoint.value : null
  })

  const data = {
    labels: allYears.map(year => year.toString()),
    datasets: [
      {
        label: country1Name,
        data: country1Values,
        borderColor: 'rgba(239, 68, 68, 1)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        borderWidth: 3,
        pointBackgroundColor: 'rgba(239, 68, 68, 1)',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 6,
        pointHoverRadius: 8,
        fill: true,
        tension: 0.1,
      },
      {
        label: country2Name,
        data: country2Values,
        borderColor: 'rgba(59, 130, 246, 1)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 3,
        pointBackgroundColor: 'rgba(59, 130, 246, 1)',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 6,
        pointHoverRadius: 8,
        fill: true,
        tension: 0.1,
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
            const value = context.parsed.y
            if (value === null) return `${context.dataset.label}: No data`
            return `${context.dataset.label}: ${formatValue(value, indicator)}`
          }
        }
      },
    },
    scales: {
      x: {
        grid: {
          color: '#334155',
          drawBorder: false,
        },
        ticks: {
          color: '#64748b',
          font: {
            family: 'Inter',
            size: 11,
          },
        },
        title: {
          display: true,
          text: 'Year',
          color: '#e2e8f0',
          font: {
            family: 'Inter',
            size: 12,
            weight: '500',
          },
        },
      },
      y: {
        grid: {
          color: '#334155',
          drawBorder: false,
        },
        ticks: {
          color: '#64748b',
          font: {
            family: 'Inter',
            size: 11,
          },
          callback: function(value) {
            return formatValue(value, indicator)
          }
        },
        title: {
          display: true,
          text: indicatorLabels[indicator] || indicator,
          color: '#e2e8f0',
          font: {
            family: 'Inter',
            size: 12,
            weight: '500',
          },
        },
      },
    },
    interaction: {
      intersect: false,
      mode: 'index',
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
        <h3 className="text-xl font-semibold text-white mb-2">Historical Trends</h3>
        <p className="text-dark-400 text-sm">
          {indicatorLabels[indicator] || indicator} over the last 10 years
        </p>
      </div>
      
      <div className="h-96">
        <Line data={data} options={options} />
      </div>
      
      <div className="mt-4 p-4 bg-dark-700 rounded-lg">
        <p className="text-dark-300 text-xs">
          <strong>Note:</strong> Historical data is sourced from the World Bank API. 
          Some data points may be missing for certain years.
        </p>
      </div>
    </div>
  )
}

export default LineChart
