import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navigation from './components/Navigation'
import Dashboard from './pages/Dashboard'
import StrategyEditor from './pages/StrategyEditor'
import DNSETrading from './pages/DNSETrading'

function App() {
  const [currentTab, setCurrentTab] = useState('dashboard')

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Navigation currentTab={currentTab} setCurrentTab={setCurrentTab} />
      
      <div className="container mx-auto px-4 py-6">
        {currentTab === 'dashboard' && <Dashboard />}
        {currentTab === 'strategy-editor' && <StrategyEditor />}
        {currentTab === 'dnse-trading' && <DNSETrading />}
      </div>
    </div>
  )
}

export default App
