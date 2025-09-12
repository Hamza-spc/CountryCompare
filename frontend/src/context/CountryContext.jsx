import React, { createContext, useContext, useReducer, useEffect } from 'react'
import { countryAPI } from '../services/api'

const CountryContext = createContext()

const initialState = {
  countries: [],
  loading: false,
  error: null,
  selectedCountries: {
    country1: null,
    country2: null
  },
  comparison: null,
  comparisonLoading: false,
  comparisonError: null
}

function countryReducer(state, action) {
  switch (action.type) {
    case 'FETCH_COUNTRIES_START':
      return { ...state, loading: true, error: null }
    
    case 'FETCH_COUNTRIES_SUCCESS':
      return { ...state, loading: false, countries: action.payload }
    
    case 'FETCH_COUNTRIES_ERROR':
      return { ...state, loading: false, error: action.payload }
    
    case 'SELECT_COUNTRY':
      return {
        ...state,
        selectedCountries: {
          ...state.selectedCountries,
          [action.payload.type]: action.payload.country
        }
      }
    
    case 'COMPARE_COUNTRIES_START':
      return { ...state, comparisonLoading: true, comparisonError: null }
    
    case 'COMPARE_COUNTRIES_SUCCESS':
      return { ...state, comparisonLoading: false, comparison: action.payload }
    
    case 'COMPARE_COUNTRIES_ERROR':
      return { ...state, comparisonLoading: false, comparisonError: action.payload }
    
    case 'CLEAR_COMPARISON':
      return { ...state, comparison: null, comparisonError: null }
    
    default:
      return state
  }
}

export function CountryProvider({ children }) {
  const [state, dispatch] = useReducer(countryReducer, initialState)

  useEffect(() => {
    fetchCountries()
  }, [])

  const fetchCountries = async () => {
    dispatch({ type: 'FETCH_COUNTRIES_START' })
    try {
      const countries = await countryAPI.getCountries()
      dispatch({ type: 'FETCH_COUNTRIES_SUCCESS', payload: countries })
    } catch (error) {
      dispatch({ type: 'FETCH_COUNTRIES_ERROR', payload: error.message })
    }
  }

  const selectCountry = (type, country) => {
    dispatch({ type: 'SELECT_COUNTRY', payload: { type, country } })
  }

  const compareCountries = async (country1, country2) => {
    dispatch({ type: 'COMPARE_COUNTRIES_START' })
    try {
      const comparison = await countryAPI.compareCountries(country1, country2)
      dispatch({ type: 'COMPARE_COUNTRIES_SUCCESS', payload: comparison })
    } catch (error) {
      dispatch({ type: 'COMPARE_COUNTRIES_ERROR', payload: error.message })
    }
  }

  const clearComparison = () => {
    dispatch({ type: 'CLEAR_COMPARISON' })
  }

  const value = {
    ...state,
    selectCountry,
    compareCountries,
    clearComparison,
    fetchCountries
  }

  return (
    <CountryContext.Provider value={value}>
      {children}
    </CountryContext.Provider>
  )
}

export function useCountry() {
  const context = useContext(CountryContext)
  if (!context) {
    throw new Error('useCountry must be used within a CountryProvider')
  }
  return context
}
