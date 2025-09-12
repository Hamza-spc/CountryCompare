import React from 'react'
import { 
  Users, 
  MapPin, 
  DollarSign, 
  TrendingUp, 
  Heart, 
  Wifi, 
  Award,
  ArrowUp,
  ArrowDown,
  Minus
} from 'lucide-react'

function ComparisonMetrics({ comparison, country1Name, country2Name }) {
  if (!comparison || !comparison.comparison_metrics) {
    return null
  }

  const metrics = comparison.comparison_metrics

  const formatValue = (value, type) => {
    if (value === null || value === undefined) return 'N/A'
    
    switch (type) {
      case 'population':
        return (value / 1000000).toFixed(1) + 'M'
      case 'area':
        return value.toLocaleString() + ' km²'
      case 'gdp':
        return '$' + (value / 1000000000).toFixed(1) + 'B'
      case 'gdp_per_capita':
        return '$' + value.toLocaleString()
      case 'hdi':
        return value.toFixed(3)
      case 'life_expectancy':
        return value.toFixed(1) + ' years'
      case 'internet_penetration':
        return value.toFixed(1) + '%'
      default:
        return value.toString()
    }
  }

  const getComparisonIcon = (country1Value, country2Value, type) => {
    if (country1Value > country2Value) {
      return <ArrowUp className="h-4 w-4 text-green-500" />
    } else if (country1Value < country2Value) {
      return <ArrowDown className="h-4 w-4 text-red-500" />
    } else {
      return <Minus className="h-4 w-4 text-gray-500" />
    }
  }

  const metricsData = [
    {
      key: 'population',
      label: 'Population',
      icon: Users,
      description: 'Total population'
    },
    {
      key: 'area',
      label: 'Area',
      icon: MapPin,
      description: 'Total land area'
    },
    {
      key: 'gdp',
      label: 'GDP',
      icon: DollarSign,
      description: 'Gross Domestic Product'
    },
    {
      key: 'gdp_per_capita',
      label: 'GDP per Capita',
      icon: TrendingUp,
      description: 'GDP per person'
    },
    {
      key: 'hdi',
      label: 'HDI',
      icon: Award,
      description: 'Human Development Index'
    },
    {
      key: 'life_expectancy',
      label: 'Life Expectancy',
      icon: Heart,
      description: 'Average life expectancy'
    },
    {
      key: 'internet_penetration',
      label: 'Internet Penetration',
      icon: Wifi,
      description: 'Internet users percentage'
    }
  ]

  return (
    <div className="chart-container">
      <div className="mb-6">
        <h3 className="text-xl font-semibold text-white mb-2">Detailed Metrics Comparison</h3>
        <p className="text-dark-400 text-sm">
          Side-by-side comparison of key indicators between {country1Name} and {country2Name}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {metricsData.map((metric) => {
          const Icon = metric.icon
          const country1Value = metrics[metric.key]?.country1
          const country2Value = metrics[metric.key]?.country2
          const winner = metrics[metric.key]?.winner

          return (
            <div key={metric.key} className="metric-card">
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 bg-primary-600 rounded-lg">
                  <Icon className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h4 className="text-white font-semibold">{metric.label}</h4>
                  <p className="text-dark-400 text-sm">{metric.description}</p>
                </div>
              </div>

              <div className="space-y-4">
                {/* Country 1 */}
                <div className="flex items-center justify-between p-3 bg-dark-700 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <span className="text-sm font-medium text-dark-300">{country1Name}</span>
                    {getComparisonIcon(country1Value, country2Value, metric.key)}
                  </div>
                  <span className="text-white font-semibold">
                    {formatValue(country1Value, metric.key)}
                  </span>
                </div>

                {/* Country 2 */}
                <div className="flex items-center justify-between p-3 bg-dark-700 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <span className="text-sm font-medium text-dark-300">{country2Name}</span>
                    {getComparisonIcon(country2Value, country1Value, metric.key)}
                  </div>
                  <span className="text-white font-semibold">
                    {formatValue(country2Value, metric.key)}
                  </span>
                </div>

                {/* Winner */}
                <div className="flex items-center justify-between p-3 bg-gradient-to-r from-primary-600/20 to-primary-700/20 border border-primary-500/30 rounded-lg">
                  <span className="text-sm font-medium text-primary-300">Winner</span>
                  <span className="text-primary-400 font-semibold">
                    {winner || 'Tie'}
                  </span>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default ComparisonMetrics
