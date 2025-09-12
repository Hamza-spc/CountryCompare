import React from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, BarChart3, Globe, TrendingUp, Users, DollarSign } from 'lucide-react'

function Home() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="text-center py-16 lg:py-24">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl lg:text-6xl font-bold text-white mb-6">
            Compare Countries
            <span className="text-gradient block">Worldwide</span>
          </h1>
          <p className="text-xl text-dark-300 mb-8 max-w-2xl mx-auto">
            Discover insights about countries across the globe. Compare economic indicators, 
            social metrics, and technology adoption in an interactive and visual way.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              to="/compare" 
              className="btn-primary inline-flex items-center space-x-2 px-8 py-4 text-lg"
            >
              <span>Start Comparing</span>
              <ArrowRight className="h-5 w-5" />
            </Link>
            <button className="btn-secondary inline-flex items-center space-x-2 px-8 py-4 text-lg">
              <Globe className="h-5 w-5" />
              <span>Explore Countries</span>
            </button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            What You Can Compare
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Economy Card */}
            <div className="card group hover:scale-105 transition-transform duration-300">
              <div className="flex items-center space-x-4 mb-4">
                <div className="p-3 bg-green-600 rounded-lg group-hover:bg-green-700 transition-colors">
                  <DollarSign className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-white">Economy</h3>
              </div>
              <p className="text-dark-300 mb-4">
                Compare GDP, GDP per capita, inflation rates, and currency information.
              </p>
              <ul className="space-y-2 text-sm text-dark-400">
                <li>• Gross Domestic Product</li>
                <li>• GDP per Capita</li>
                <li>• Economic Growth</li>
                <li>• Currency Exchange</li>
              </ul>
            </div>

            {/* Social Indicators Card */}
            <div className="card group hover:scale-105 transition-transform duration-300">
              <div className="flex items-center space-x-4 mb-4">
                <div className="p-3 bg-blue-600 rounded-lg group-hover:bg-blue-700 transition-colors">
                  <Users className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-white">Social</h3>
              </div>
              <p className="text-dark-300 mb-4">
                Analyze Human Development Index, life expectancy, and literacy rates.
              </p>
              <ul className="space-y-2 text-sm text-dark-400">
                <li>• Human Development Index</li>
                <li>• Life Expectancy</li>
                <li>• Literacy Rate</li>
                <li>• Education Quality</li>
              </ul>
            </div>

            {/* Technology Card */}
            <div className="card group hover:scale-105 transition-transform duration-300">
              <div className="flex items-center space-x-4 mb-4">
                <div className="p-3 bg-purple-600 rounded-lg group-hover:bg-purple-700 transition-colors">
                  <TrendingUp className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-white">Technology</h3>
              </div>
              <p className="text-dark-300 mb-4">
                Explore internet penetration, innovation indices, and digital adoption.
              </p>
              <ul className="space-y-2 text-sm text-dark-400">
                <li>• Internet Penetration</li>
                <li>• Innovation Index</li>
                <li>• Digital Infrastructure</li>
                <li>• Tech Adoption</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-16 bg-dark-800/50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            How It Works
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-white">1</span>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Select Countries</h3>
              <p className="text-dark-300">
                Choose any two countries from our comprehensive database of 195+ nations.
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-white">2</span>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Compare Data</h3>
              <p className="text-dark-300">
                View side-by-side comparisons with interactive charts and detailed metrics.
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-white">3</span>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Analyze Results</h3>
              <p className="text-dark-300">
                Gain insights through visual charts and comprehensive data analysis.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 text-center">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-white mb-6">
            Ready to Start Comparing?
          </h2>
          <p className="text-xl text-dark-300 mb-8">
            Discover fascinating insights about countries around the world.
          </p>
          <Link 
            to="/compare" 
            className="btn-primary inline-flex items-center space-x-2 px-8 py-4 text-lg glow"
          >
            <BarChart3 className="h-5 w-5" />
            <span>Compare Countries Now</span>
          </Link>
        </div>
      </section>
    </div>
  )
}

export default Home
