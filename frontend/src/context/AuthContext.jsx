import React, { createContext, useContext, useReducer, useEffect } from 'react'
import { authAPI } from '../services/api'

const AuthContext = createContext()

const initialState = {
  user: null,
  token: localStorage.getItem('token'),
  loading: false,
  error: null,
  isAuthenticated: false
}

function authReducer(state, action) {
  switch (action.type) {
    case 'AUTH_START':
      return { ...state, loading: true, error: null }
    
    case 'AUTH_SUCCESS':
      return {
        ...state,
        loading: false,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        error: null
      }
    
    case 'AUTH_ERROR':
      return {
        ...state,
        loading: false,
        error: action.payload,
        isAuthenticated: false
      }
    
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        error: null
      }
    
    case 'CLEAR_ERROR':
      return { ...state, error: null }
    
    default:
      return state
  }
}

export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, initialState)

  useEffect(() => {
    if (state.token) {
      // Verify token on app load
      verifyToken()
    }
  }, [])

  const verifyToken = async () => {
    try {
      // This would typically verify the token with the backend
      // For now, we'll just check if it exists
      if (state.token) {
        dispatch({
          type: 'AUTH_SUCCESS',
          payload: { user: { username: 'User' }, token: state.token }
        })
      }
    } catch (error) {
      dispatch({ type: 'AUTH_ERROR', payload: 'Token verification failed' })
      localStorage.removeItem('token')
    }
  }

  const login = async (username, password) => {
    dispatch({ type: 'AUTH_START' })
    try {
      const response = await authAPI.login(username, password)
      localStorage.setItem('token', response.access_token)
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: { user: response.user, token: response.access_token }
      })
      return response
    } catch (error) {
      dispatch({ type: 'AUTH_ERROR', payload: error.message })
      throw error
    }
  }

  const register = async (username, email, password) => {
    dispatch({ type: 'AUTH_START' })
    try {
      const response = await authAPI.register(username, email, password)
      localStorage.setItem('token', response.access_token)
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: { user: response.user, token: response.access_token }
      })
      return response
    } catch (error) {
      dispatch({ type: 'AUTH_ERROR', payload: error.message })
      throw error
    }
  }

  const googleAuth = async (token) => {
    dispatch({ type: 'AUTH_START' })
    try {
      const response = await authAPI.googleAuth(token)
      localStorage.setItem('token', response.access_token)
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: { user: response.user, token: response.access_token }
      })
      return response
    } catch (error) {
      dispatch({ type: 'AUTH_ERROR', payload: error.message })
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    dispatch({ type: 'LOGOUT' })
  }

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' })
  }

  const value = {
    ...state,
    login,
    register,
    googleAuth,
    logout,
    clearError
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
