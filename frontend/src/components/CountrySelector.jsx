import React, { useState, useMemo } from 'react'
import { Search, ChevronDown, MapPin } from 'lucide-react'

function CountrySelector({ 
  countries, 
  selectedCountry, 
  onSelect, 
  placeholder = "Select a country...",
  disabled = false 
}) {
  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')

  const filteredCountries = useMemo(() => {
    if (!searchTerm) return countries // Show all countries when no search term
    
    return countries
      .filter(country => 
        country.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        country.capital.toLowerCase().includes(searchTerm.toLowerCase()) ||
        country.region.toLowerCase().includes(searchTerm.toLowerCase())
      )
  }, [countries, searchTerm])

  const handleSelect = (country) => {
    onSelect(country)
    setIsOpen(false)
    setSearchTerm('')
  }

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        disabled={disabled}
        className={`w-full flex items-center justify-between px-4 py-3 bg-dark-800 border border-dark-600 rounded-lg text-left transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
          disabled 
            ? 'opacity-50 cursor-not-allowed' 
            : 'hover:border-dark-500 cursor-pointer'
        }`}
      >
        <div className="flex items-center space-x-3">
          {selectedCountry ? (
            <>
              <img 
                src={selectedCountry.flag_url} 
                alt={`${selectedCountry.name} flag`}
                className="h-6 w-8 object-cover rounded-sm"
                onError={(e) => {
                  e.target.style.display = 'none'
                }}
              />
              <div>
                <p className="text-white font-medium">{selectedCountry.name}</p>
                <p className="text-dark-400 text-sm">{selectedCountry.capital}, {selectedCountry.region}</p>
              </div>
            </>
          ) : (
            <div className="flex items-center space-x-3">
              <MapPin className="h-5 w-5 text-dark-400" />
              <span className="text-dark-400">{placeholder}</span>
            </div>
          )}
        </div>
        <ChevronDown className={`h-5 w-5 text-dark-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-dark-800 border border-dark-600 rounded-lg shadow-xl z-50 max-h-80 overflow-hidden">
          <div className="p-3 border-b border-dark-700">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-dark-400" />
              <input
                type="text"
                placeholder="Search countries..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-dark-900 border border-dark-600 rounded-lg text-white placeholder-dark-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                autoFocus
              />
            </div>
          </div>
          
          <div className="max-h-60 overflow-y-auto">
            {filteredCountries.length === 0 ? (
              <div className="p-4 text-center text-dark-400">
                No countries found
              </div>
            ) : (
              filteredCountries.map((country) => (
                <button
                  key={country.id || country.name}
                  onClick={() => handleSelect(country)}
                  className="w-full flex items-center space-x-3 p-3 hover:bg-dark-700 transition-colors text-left"
                >
                  <img 
                    src={country.flag_url} 
                    alt={`${country.name} flag`}
                    className="h-6 w-8 object-cover rounded-sm"
                    onError={(e) => {
                      e.target.style.display = 'none'
                    }}
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-white font-medium truncate">{country.name}</p>
                    <p className="text-dark-400 text-sm truncate">{country.capital}, {country.region}</p>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      )}

      {/* Overlay to close dropdown when clicking outside */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  )
}

export default CountrySelector
