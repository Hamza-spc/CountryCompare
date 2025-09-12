import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Globe, BarChart3 } from 'lucide-react'

function Header() {
  const location = useLocation()

  return (
    <header className="bg-dark-800 border-b border-dark-700 sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 group">
            <div className="p-2 bg-primary-600 rounded-lg group-hover:bg-primary-700 transition-colors">
              <Globe className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gradient">CountryCompare</h1>
              <p className="text-xs text-dark-400">Compare countries worldwide</p>
            </div>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center space-x-1">
            <Link
              to="/"
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                location.pathname === '/'
                  ? 'bg-primary-600 text-white'
                  : 'text-dark-300 hover:text-white hover:bg-dark-700'
              }`}
            >
              <Globe className="h-4 w-4" />
              <span>Home</span>
            </Link>
            
            <Link
              to="/compare"
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                location.pathname === '/compare'
                  ? 'bg-primary-600 text-white'
                  : 'text-dark-300 hover:text-white hover:bg-dark-700'
              }`}
            >
              <BarChart3 className="h-4 w-4" />
              <span>Compare</span>
            </Link>
          </nav>
        </div>
      </div>
    </header>
  )
}

export default Header
