import React, { useState, useEffect } from 'react'
import { useCountry } from '../context/CountryContext'
import CountrySelector from '../components/CountrySelector'
import LoadingSpinner from '../components/LoadingSpinner'
import RadarChart from '../components/charts/RadarChart'
import BarChart from '../components/charts/BarChart'
import ComparisonMetrics from '../components/charts/ComparisonMetrics'
import { ArrowRight, RotateCcw, AlertCircle } from 'lucide-react'

function Compare() {
  const { 
    countries, 
    loading, 
    error, 
    selectedCountries, 
    comparison, 
    comparisonLoading, 
    comparisonError,
    selectCountry, 
    compareCountries, 
    clearComparison 
  } = useCountry()

  const [canCompare, setCanCompare] = useState(false)

  useEffect(() => {
    setCanCompare(
      selectedCountries.country1 && 
      selectedCountries.country2 && 
      selectedCountries.country1.name !== selectedCountries.country2.name
    )
  }, [selectedCountries])

  const handleCompare = async () => {
    if (!canCompare) return
    
    await compareCountries(
      selectedCountries.country1.name, 
      selectedCountries.country2.name
    )
  }

  const handleReset = () => {
    selectCountry('country1', null)
    selectCountry('country2', null)
    clearComparison()
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-96">
        <LoadingSpinner size="lg" text="Loading countries..." />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-16">
        <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
        <h2 className="text-2xl font-semibold text-white mb-2">Error Loading Countries</h2>
        <p className="text-dark-400 mb-6">{error}</p>
        <button 
          onClick={() => window.location.reload()} 
          className="btn-primary"
        >
          Try Again
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-white mb-4">
          Compare Countries
        </h1>
        <p className="text-xl text-dark-300 max-w-2xl mx-auto">
          Select two countries to compare their key indicators including economy, 
          social metrics, and technology adoption.
        </p>
      </div>

      {/* Country Selection */}
      <div className="card mb-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              First Country
            </label>
            <CountrySelector
              countries={countries}
              selectedCountry={selectedCountries.country1}
              onSelect={(country) => selectCountry('country1', country)}
              placeholder="Select first country..."
              disabled={comparisonLoading}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              Second Country
            </label>
            <CountrySelector
              countries={countries}
              selectedCountry={selectedCountries.country2}
              onSelect={(country) => selectCountry('country2', country)}
              placeholder="Select second country..."
              disabled={comparisonLoading}
            />
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={handleCompare}
            disabled={!canCompare || comparisonLoading}
            className={`btn-primary flex items-center space-x-2 ${
              !canCompare || comparisonLoading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {comparisonLoading ? (
              <>
                <LoadingSpinner size="sm" text="" />
                <span>Comparing...</span>
              </>
            ) : (
              <>
                <ArrowRight className="h-4 w-4" />
                <span>Compare Countries</span>
              </>
            )}
          </button>
          
          {(selectedCountries.country1 || selectedCountries.country2 || comparison) && (
            <button
              onClick={handleReset}
              disabled={comparisonLoading}
              className="btn-secondary flex items-center space-x-2"
            >
              <RotateCcw className="h-4 w-4" />
              <span>Reset</span>
            </button>
          )}
        </div>

        {!canCompare && selectedCountries.country1 && selectedCountries.country2 && (
          <div className="mt-4 p-3 bg-yellow-600/20 border border-yellow-500/30 rounded-lg">
            <p className="text-yellow-400 text-sm text-center">
              Please select two different countries to compare.
            </p>
          </div>
        )}
      </div>

      {/* Comparison Error */}
      {comparisonError && (
        <div className="card mb-8 border-red-500/30 bg-red-600/10">
          <div className="flex items-center space-x-3">
            <AlertCircle className="h-5 w-5 text-red-500" />
            <div>
              <h3 className="text-red-400 font-semibold">Comparison Failed</h3>
              <p className="text-red-300 text-sm">{comparisonError}</p>
            </div>
          </div>
        </div>
      )}

      {/* Comparison Results */}
      {comparison && (
        <div className="space-y-8">
          {/* Country Info Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Country 1 Card */}
            <div className="card">
              <div className="flex items-center space-x-4 mb-4">
                <img 
                  src={comparison.country1.flag_url} 
                  alt={`${comparison.country1.name} flag`}
                  className="h-12 w-16 object-cover rounded-lg"
                  onError={(e) => {
                    e.target.style.display = 'none'
                  }}
                />
                <div>
                  <h3 className="text-xl font-semibold text-white">{comparison.country1.name}</h3>
                  <p className="text-dark-400">{comparison.country1.capital}, {comparison.country1.region}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-dark-400">Population</p>
                  <p className="text-white font-semibold">
                    {(comparison.country1.population / 1000000).toFixed(1)}M
                  </p>
                </div>
                <div>
                  <p className="text-dark-400">Area</p>
                  <p className="text-white font-semibold">
                    {comparison.country1.area.toLocaleString()} km²
                  </p>
                </div>
              </div>
            </div>

            {/* Country 2 Card */}
            <div className="card">
              <div className="flex items-center space-x-4 mb-4">
                <img 
                  src={comparison.country2.flag_url} 
                  alt={`${comparison.country2.name} flag`}
                  className="h-12 w-16 object-cover rounded-lg"
                  onError={(e) => {
                    e.target.style.display = 'none'
                  }}
                />
                <div>
                  <h3 className="text-xl font-semibold text-white">{comparison.country2.name}</h3>
                  <p className="text-dark-400">{comparison.country2.capital}, {comparison.country2.region}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-dark-400">Population</p>
                  <p className="text-white font-semibold">
                    {(comparison.country2.population / 1000000).toFixed(1)}M
                  </p>
                </div>
                <div>
                  <p className="text-dark-400">Area</p>
                  <p className="text-white font-semibold">
                    {comparison.country2.area.toLocaleString()} km²
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
            <RadarChart 
              comparison={comparison} 
              country1Name={comparison.country1.name}
              country2Name={comparison.country2.name}
            />
            <BarChart 
              comparison={comparison} 
              country1Name={comparison.country1.name}
              country2Name={comparison.country2.name}
            />
          </div>

          {/* Detailed Metrics */}
          <ComparisonMetrics 
            comparison={comparison} 
            country1Name={comparison.country1.name}
            country2Name={comparison.country2.name}
          />
        </div>
      )}

      {/* Empty State */}
      {!comparison && !comparisonLoading && (
        <div className="text-center py-16">
          <div className="w-24 h-24 bg-dark-700 rounded-full flex items-center justify-center mx-auto mb-6">
            <ArrowRight className="h-12 w-12 text-dark-400" />
          </div>
          <h3 className="text-xl font-semibold text-white mb-2">Ready to Compare?</h3>
          <p className="text-dark-400 mb-6">
            Select two countries above to see detailed comparisons and insights.
          </p>
        </div>
      )}
    </div>
  )
}

export default Compare
