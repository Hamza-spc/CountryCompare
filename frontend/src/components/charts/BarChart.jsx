import React from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

function BarChart({ comparison, country1Name, country2Name }) {
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

  // Create bar chart data for key economic indicators
  const economicData = {
    labels: ['GDP (Billion USD)', 'GDP per Capita (USD)', 'Population (Millions)'],
    datasets: [
      {
        label: country1Name,
        data: [
          (metrics.gdp?.country1 || 0) / 1000000000, // Convert to billions
          metrics.gdp_per_capita?.country1 || 0,
          (metrics.population?.country1 || 0) / 1000000 // Convert to millions
        ],
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      },
      {
        label: country2Name,
        data: [
          (metrics.gdp?.country2 || 0) / 1000000000, // Convert to billions
          metrics.gdp_per_capita?.country2 || 0,
          (metrics.population?.country2 || 0) / 1000000 // Convert to millions
        ],
        backgroundColor: 'rgba(16, 185, 129, 0.8)',
        borderColor: 'rgba(16, 185, 129, 1)',
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
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
          pointStyle: 'rect',
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
            const label = context.dataset.label
            const value = context.parsed.y
            const metricIndex = context.dataIndex
            
            let formattedValue
            if (metricIndex === 0) { // GDP
              formattedValue = '$' + value.toFixed(1) + 'B'
            } else if (metricIndex === 1) { // GDP per capita
              formattedValue = '$' + value.toLocaleString()
            } else { // Population
              formattedValue = value.toFixed(1) + 'M'
            }
            
            return `${label}: ${formattedValue}`
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
          maxRotation: 45,
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
          callback: function(value, index, ticks) {
            if (index === 0) { // GDP
              return '$' + value.toFixed(1) + 'B'
            } else if (index === 1) { // GDP per capita
              return '$' + value.toLocaleString()
            } else { // Population
              return value.toFixed(1) + 'M'
            }
          }
        },
      },
    },
    interaction: {
      intersect: false,
      mode: 'index',
    },
  }

  return (
    <div className="chart-container">
      <div className="mb-6">
        <h3 className="text-xl font-semibold text-white mb-2">Economic Indicators Comparison</h3>
        <p className="text-dark-400 text-sm">
          Compare GDP, GDP per capita, and population between the two countries
        </p>
      </div>
      
      <div className="h-96">
        <Bar data={economicData} options={options} />
      </div>
      
      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-3 bg-dark-700 rounded-lg">
          <h4 className="text-sm font-medium text-white mb-1">GDP Winner</h4>
          <p className="text-primary-400 font-semibold">
            {metrics.gdp?.winner || 'N/A'}
          </p>
        </div>
        <div className="p-3 bg-dark-700 rounded-lg">
          <h4 className="text-sm font-medium text-white mb-1">GDP per Capita Winner</h4>
          <p className="text-primary-400 font-semibold">
            {metrics.gdp_per_capita?.winner || 'N/A'}
          </p>
        </div>
        <div className="p-3 bg-dark-700 rounded-lg">
          <h4 className="text-sm font-medium text-white mb-1">Population Winner</h4>
          <p className="text-primary-400 font-semibold">
            {metrics.population?.winner || 'N/A'}
          </p>
        </div>
      </div>
    </div>
  )
}

export default BarChart
