import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navigation from './components/Navigation'
import Dashboard from './pages/Dashboard'
import StrategyEditor from './pages/StrategyEditor'
import DNSETrading from './pages/DNSETrading'
import OrderList from './pages/OrderList'

function App() {
  const [currentTab, setCurrentTab] = useState('dashboard')
  const [authData, setAuthData] = useState({
    isAuthenticated: false,
    hasTradingToken: false,
    userInfo: null,
    tradingToken: null,
    accounts: []
  })

  // Handle authentication data from DNSETrading component
  const handleAuthChange = (data) => {
    setAuthData(data)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Navigation currentTab={currentTab} setCurrentTab={setCurrentTab} />
      
      <div className="container mx-auto px-4 py-6">
        {currentTab === 'dashboard' && <Dashboard />}
        {currentTab === 'strategy-editor' && <StrategyEditor />}
        {currentTab === 'dnse-trading' && <DNSETrading onAuthChange={handleAuthChange} />}
        {currentTab === 'orders' && <OrderList authData={authData} />}
      </div>
    </div>
  )
}

export default App
