import React, { useState, useEffect } from 'react'
import { Activity, TrendingUp, TrendingDown, DollarSign, PieChart, Calendar } from 'lucide-react'
import Plot from 'react-plotly.js'

const Dashboard = () => {
  const [marketData, setMarketData] = useState([])
  const [portfolio, setPortfolio] = useState({
    cash: 1000000,
    position: 0,
    totalValue: 1000000,
    pnl: 0,
    pnlPercent: 0
  })

  const [recentTrades, setRecentTrades] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [selectedSymbol, setSelectedSymbol] = useState('VCI')
  const [marketOverview, setMarketOverview] = useState([])

  // Real data loading
  useEffect(() => {
    loadRealData()
    loadMarketOverview()
    
    // Refresh data every 30 seconds
    const interval = setInterval(() => {
      loadRealData()
      loadMarketOverview()
    }, 30000)
    
    return () => clearInterval(interval)
  }, [selectedSymbol])

  const loadRealData = async () => {
    setIsLoading(true)
    try {
      // Get historical data for chart
      const response = await fetch(`/api/market/history/${selectedSymbol}?interval=1D`)
      const result = await response.json()
      
      if (result.success) {
        const formattedData = result.data.map(item => ({
          datetime: item.date,
          open: item.open,
          high: item.high,
          low: item.low,
          close: item.close,
          volume: item.volume
        }))
        setMarketData(formattedData)
      } else {
        console.error('Failed to load market data:', result.error)
        loadMockData() // Fallback to mock data
      }
    } catch (error) {
      console.error('Error loading market data:', error)
      loadMockData() // Fallback to mock data
    } finally {
      setIsLoading(false)
    }
  }

  const loadMarketOverview = async () => {
    try {
      const response = await fetch('/api/market/overview')
      const result = await response.json()
      
      if (result.success) {
        setMarketOverview(result.data)
      }
    } catch (error) {
      console.error('Error loading market overview:', error)
    }
  }

  const refreshData = () => {
    loadRealData()
    loadMarketOverview()
  }

  const loadMockData = () => {
    // Generate mock market data
    const data = []
    const basePrice = 25000
    const now = new Date()
    
    for (let i = 100; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 60 * 1000)
      const price = basePrice + (Math.random() - 0.5) * 1000
      data.push({
        datetime: time.toISOString(),
        open: price,
        high: price + Math.random() * 500,
        low: price - Math.random() * 500,
        close: price + (Math.random() - 0.5) * 200,
        volume: Math.floor(Math.random() * 100000)
      })
    }
    
    setMarketData(data)
    
    // Mock recent trades
    setRecentTrades([
      { type: 'buy', symbol: 'VCI', quantity: 100, price: 24800, time: '10:30:15' },
      { type: 'sell', symbol: 'VCI', quantity: 50, price: 25200, time: '11:45:22' },
      { type: 'buy', symbol: 'ACB', quantity: 200, price: 23500, time: '14:20:08' }
    ])
  }

  const portfolioMetrics = [
    {
      label: 'Total Value',
      value: portfolio.totalValue.toLocaleString() + ' VND',
      icon: DollarSign,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      label: 'Cash',
      value: portfolio.cash.toLocaleString() + ' VND',
      icon: Activity,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      label: 'Position',
      value: portfolio.position.toString() + ' shares',
      icon: PieChart,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    },
    {
      label: 'P&L',
      value: portfolio.pnl.toLocaleString() + ' VND (' + portfolio.pnlPercent.toFixed(2) + '%)',
      icon: portfolio.pnl >= 0 ? TrendingUp : TrendingDown,
      color: portfolio.pnl >= 0 ? 'text-green-600' : 'text-red-600',
      bgColor: portfolio.pnl >= 0 ? 'bg-green-50' : 'bg-red-50'
    }
  ]

  const chartData = marketData.length > 0 ? [{
    x: marketData.map(d => d.datetime),
    close: marketData.map(d => d.close),
    high: marketData.map(d => d.high),
    low: marketData.map(d => d.low),
    open: marketData.map(d => d.open),
    type: 'candlestick',
    name: 'Price',
    increasing: { line: { color: '#27ae60' } },
    decreasing: { line: { color: '#e74c3c' } }
  }] : []

  const chartLayout = {
    title: `Market Data - ${selectedSymbol}`,
    xaxis: { title: 'Time', rangeslider: { visible: false } },
    yaxis: { title: 'Price (VND)' },
    height: 400,
    margin: { t: 50, b: 50, l: 50, r: 50 }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <Activity className="h-6 w-6 mr-2 text-primary" />
              Trading Dashboard
            </h1>
            <p className="text-gray-600">Monitor your trading performance and market data</p>
          </div>
          
          <div className="flex space-x-2">
            <select 
              value={selectedSymbol} 
              onChange={(e) => setSelectedSymbol(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="VCI">VCI</option>
              <option value="VCB">VCB</option>
              <option value="HPG">HPG</option>
              <option value="MSN">MSN</option>
              <option value="TCB">TCB</option>
              <option value="VIC">VIC</option>
              <option value="FPT">FPT</option>
              <option value="VHM">VHM</option>
              <option value="POW">POW</option>
              <option value="ACB">ACB</option>
            </select>
            <button 
              onClick={refreshData}
              disabled={isLoading}
              className="btn btn-primary"
            >
              <Activity className="h-4 w-4 mr-2" />
              {isLoading ? 'Loading...' : 'Refresh Data'}
            </button>
          </div>
        </div>
      </div>

      {/* Portfolio Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {portfolioMetrics.map((metric, index) => {
          const Icon = metric.icon
          return (
            <div key={index} className={`card ${metric.bgColor} border-l-4 border-current`}>
              <div className="flex items-center">
                <div className={`p-3 rounded-full ${metric.bgColor}`}>
                  <Icon className={`h-6 w-6 ${metric.color}`} />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{metric.label}</p>
                  <p className={`text-lg font-bold ${metric.color}`}>{metric.value}</p>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Market Overview */}
      {marketOverview.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Market Overview</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {marketOverview.map((stock, index) => (
              <div 
                key={index} 
                className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                  selectedSymbol === stock.symbol 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedSymbol(stock.symbol)}
              >
                <div className="text-center">
                  <p className="font-semibold text-sm">{stock.symbol}</p>
                  <p className="text-lg font-bold text-gray-900">
                    {stock.price ? stock.price.toLocaleString() : 'N/A'}
                  </p>
                  <p className={`text-sm ${
                    stock.change >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {stock.change >= 0 ? '+' : ''}{stock.change_percent ? stock.change_percent.toFixed(2) : '0.00'}%
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chart */}
        <div className="lg:col-span-2 card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Price Chart</h3>
          {marketData.length > 0 ? (
            <Plot
              data={chartData}
              layout={chartLayout}
              style={{ width: '100%', height: '400px' }}
              useResizeHandler={true}
            />
          ) : (
            <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
              <p className="text-gray-500">No market data available</p>
            </div>
          )}
        </div>

        {/* Recent Trades */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Trades</h3>
          <div className="space-y-3">
            {recentTrades.length > 0 ? (
              recentTrades.map((trade, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className={`px-2 py-1 rounded text-xs font-medium ${
                      trade.type === 'buy' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {trade.type.toUpperCase()}
                    </div>
                    <div>
                      <p className="font-medium text-sm">{trade.symbol}</p>
                      <p className="text-xs text-gray-500">{trade.quantity} shares</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-sm">{trade.price.toLocaleString()}</p>
                    <p className="text-xs text-gray-500">{trade.time}</p>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Calendar className="h-8 w-8 mx-auto mb-2" />
                <p>No trades yet</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="btn btn-primary justify-center">
            <Activity className="h-4 w-4 mr-2" />
            Start Trading
          </button>
          <button className="btn btn-success justify-center">
            <TrendingUp className="h-4 w-4 mr-2" />
            Run Backtest
          </button>
          <button className="btn btn-warning justify-center">
            <PieChart className="h-4 w-4 mr-2" />
            Portfolio Analysis
          </button>
          <button className="btn btn-secondary justify-center">
            <Calendar className="h-4 w-4 mr-2" />
            View History
          </button>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
