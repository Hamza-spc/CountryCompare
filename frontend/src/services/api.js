import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

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

  async getHistoricalData(countryName, indicator = 'NY.GDP.MKTP.CD', years = 10) {
    try {
      const response = await apiClient.get(`/api/historical/${countryName}`, {
        params: { indicator, years }
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch historical data')
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

export const authAPI = {
  async login(username, password) {
    try {
      const response = await apiClient.post('/api/auth/login', {
        username,
        password
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Login failed')
    }
  },

  async register(username, email, password) {
    try {
      const response = await apiClient.post('/api/auth/register', {
        username,
        email,
        password
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Registration failed')
    }
  },

  async googleAuth(token) {
    try {
      const response = await apiClient.post('/api/auth/google', {
        token
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Google authentication failed')
    }
  }
}

export const savedComparisonsAPI = {
  async getSavedComparisons() {
    try {
      const response = await apiClient.get('/api/saved-comparisons')
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch saved comparisons')
    }
  },

  async saveComparison(country1Name, country2Name, comparisonData) {
    try {
      const response = await apiClient.post('/api/saved-comparisons', {
        country1_name: country1Name,
        country2_name: country2Name,
        comparison_data: comparisonData
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to save comparison')
    }
  }
}

export const userPreferencesAPI = {
  async getPreferences() {
    try {
      const response = await apiClient.get('/api/user/preferences')
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch preferences')
    }
  },

  async updatePreferences(preferences) {
    try {
      const response = await apiClient.put('/api/user/preferences', preferences)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to update preferences')
    }
  }
}

export default apiClient
