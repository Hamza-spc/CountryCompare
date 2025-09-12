import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import Home from './pages/Home'
import Compare from './pages/Compare'
import { CountryProvider } from './context/CountryContext'

function App() {
  return (
    <CountryProvider>
      <Router>
        <div className="min-h-screen bg-dark-900">
          <Header />
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/compare" element={<Compare />} />
            </Routes>
          </main>
        </div>
      </Router>
    </CountryProvider>
  )
}

export default App
