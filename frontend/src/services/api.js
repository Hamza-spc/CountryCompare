import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export const countryAPI = {
  async getCountries() {
    try {
      const response = await apiClient.get('/api/countries')
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch countries')
    }
  },

  async getCountry(name) {
    try {
      const response = await apiClient.get(`/api/countries/${name}`)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || `Failed to fetch country: ${name}`)
    }
  },

  async compareCountries(country1, country2) {
    try {
      const response = await apiClient.get('/api/compare', {
        params: { c1: country1, c2: country2 }
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to compare countries')
    }
  },

  async healthCheck() {
    try {
      const response = await apiClient.get('/api/health')
      return response.data
    } catch (error) {
      throw new Error('API health check failed')
    }
  }
}

export default apiClient
