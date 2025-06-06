import React, { useState, useEffect } from 'react'
import { 
  User, 
  DollarSign, 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  AlertCircle,
  CheckCircle,
  Clock,
  RefreshCw,
  Send,
  X,
  Shield
} from 'lucide-react'
import DNSEAuth from '../components/DNSEAuth'

const DNSETrading = ({ onAuthChange }) => {
  // Authentication state from DNSEAuth component
  const [authData, setAuthData] = useState({
    isAuthenticated: false,
    hasTradingToken: false,
    userInfo: null,
    tradingToken: null,
    accounts: []
  })

  const [authState, setAuthState] = useState({
    isAuthenticated: false,
    hasJWT: false,
    hasTradingToken: false,
    investorInfo: null
  })
  
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  })
  
  const [otpCode, setOtpCode] = useState('')
  const [accounts, setAccounts] = useState([])
  const [selectedAccount, setSelectedAccount] = useState(null)
  const [portfolio, setPortfolio] = useState(null)
  const [buyingPower, setBuyingPower] = useState(null)
  const [pendingOrders, setPendingOrders] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  
  // Order form state
  const [orderForm, setOrderForm] = useState({
    symbol: '',
    side: 'buy',
    quantity: '',
    price: '',
    orderType: 'limit'
  })

  useEffect(() => {
    checkDNSEStatus()
  }, [])

  // Handle authentication changes from DNSEAuth component
  const handleAuthChange = (data) => {
    setAuthData(data)
    // Update legacy authState for compatibility
    setAuthState(prev => ({
      ...prev,
      isAuthenticated: data.isAuthenticated,
      hasTradingToken: data.hasTradingToken,
      investorInfo: data.userInfo
    }))
    
    // Update accounts from auth data
    if (data.accounts && data.accounts.length > 0) {
      setAccounts(data.accounts)
      if (!selectedAccount) {
        setSelectedAccount(data.accounts[0])
      }
    }
  }

  const checkDNSEStatus = async () => {
    try {
      const response = await fetch('/api/dnse/status')
      const data = await response.json()
      
      setAuthState({
        isAuthenticated: data.authenticated,
        hasJWT: data.authenticated,
        hasTradingToken: data.has_trading_token,
        investorInfo: authState.investorInfo
      })
    } catch (error) {
      console.error('Error checking DNSE status:', error)
    }
  }

  const handleLogin = async () => {
    if (!credentials.username || !credentials.password) {
      setError('Please enter username and password')
      return
    }

    setLoading(true)
    setError('')
    
    try {
      const response = await fetch('/api/dnse/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials)
      })
      
      const data = await response.json()
      
      if (data.success) {
        setAuthState({
          isAuthenticated: true,
          hasJWT: true,
          hasTradingToken: false,
          investorInfo: data.investor_info
        })
        setSuccess('Login successful! Please request OTP for trading.')
        loadAccounts()
      } else {
        setError(data.error || 'Login failed')
      }
    } catch (error) {
      setError('Network error during login')
    } finally {
      setLoading(false)
    }
  }

  const handleRequestOTP = async () => {
    setLoading(true)
    setError('')
    
    try {
      const response = await fetch('/api/dnse/request-otp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      
      const data = await response.json()
      
      if (data.success) {
        setSuccess('OTP sent to your email. Please check and enter the code.')
      } else {
        setError(data.error || 'Failed to send OTP')
      }
    } catch (error) {
      setError('Network error during OTP request')
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyOTP = async () => {
    if (!otpCode) {
      setError('Please enter OTP code')
      return
    }

    setLoading(true)
    setError('')
    
    try {
      const response = await fetch('/api/dnse/verify-otp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ otp_code: otpCode })
      })
      
      const data = await response.json()
      
      if (data.success) {
        setAuthState(prev => ({
          ...prev,
          hasTradingToken: true
        }))
        setSuccess('OTP verified! You can now place orders.')
        setOtpCode('')
      } else {
        setError(data.error || 'OTP verification failed')
      }
    } catch (error) {
      setError('Network error during OTP verification')
    } finally {
      setLoading(false)
    }
  }

  const loadAccounts = async () => {
    try {
      const response = await fetch('/api/dnse/accounts')
      const data = await response.json()
      
      if (data.success) {
        setAccounts(data.accounts)
        if (data.accounts.length > 0) {
          setSelectedAccount(data.accounts[0])
          loadAccountData(data.accounts[0].accountNo)
        }
      }
    } catch (error) {
      console.error('Error loading accounts:', error)
    }
  }

  const loadAccountData = async (accountNo) => {
    try {
      // Load portfolio
      const portfolioResponse = await fetch(`/api/dnse/portfolio/${accountNo}`)
      const portfolioData = await portfolioResponse.json()
      if (portfolioData.success) {
        setPortfolio(portfolioData.portfolio)
      }

      // Load buying power
      const buyingPowerResponse = await fetch(`/api/dnse/buying-power/${accountNo}`)
      const buyingPowerData = await buyingPowerResponse.json()
      if (buyingPowerData.success) {
        setBuyingPower(buyingPowerData.buying_power)
      }

      // Load pending orders
      const ordersResponse = await fetch(`/api/dnse/pending-orders/${accountNo}`)
      const ordersData = await ordersResponse.json()
      if (ordersData.success) {
        setPendingOrders(ordersData.orders)
      }
    } catch (error) {
      console.error('Error loading account data:', error)
    }
  }

  const handlePlaceOrder = async () => {
    if (!selectedAccount || !authState.hasTradingToken) {
      setError('Please login and verify OTP first')
      return
    }

    if (!orderForm.symbol || !orderForm.quantity || !orderForm.price) {
      setError('Please fill all order fields')
      return
    }

    setLoading(true)
    setError('')
    
    try {
      const response = await fetch('/api/dnse/place-order', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...orderForm,
          account_no: selectedAccount.accountNo,
          quantity: parseFloat(orderForm.quantity),
          price: parseFloat(orderForm.price)
        })
      })
      
      const data = await response.json()
      
      if (data.success) {
        setSuccess('Order placed successfully!')
        setOrderForm({
          symbol: '',
          side: 'buy',
          quantity: '',
          price: '',
          orderType: 'limit'
        })
        // Refresh account data
        loadAccountData(selectedAccount.accountNo)
      } else {
        setError(data.error || 'Order placement failed')
      }
    } catch (error) {
      setError('Network error during order placement')
    } finally {
      setLoading(false)
    }
  }

  const handleCancelOrder = async (orderId) => {
    if (!selectedAccount || !authState.hasTradingToken) {
      setError('Please login and verify OTP first')
      return
    }

    setLoading(true)
    setError('')
    
    try {
      const response = await fetch('/api/dnse/cancel-order', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          order_id: orderId,
          account_no: selectedAccount.accountNo
        })
      })
      
      const data = await response.json()
      
      if (data.success) {
        setSuccess('Order cancelled successfully!')
        // Refresh pending orders
        loadAccountData(selectedAccount.accountNo)
      } else {
        setError(data.error || 'Order cancellation failed')
      }
    } catch (error) {
      setError('Network error during order cancellation')
    } finally {
      setLoading(false)
    }
  }

  const refreshData = () => {
    if (selectedAccount) {
      loadAccountData(selectedAccount.accountNo)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">DNSE Trading</h1>
          <p className="text-gray-600">Real-time trading with DNSE platform</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${authState.isAuthenticated ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-sm text-gray-600">
              {authState.isAuthenticated ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          
          <button
            onClick={refreshData}
            disabled={!authState.isAuthenticated}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Alerts */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-2">
          <AlertCircle className="h-5 w-5 text-red-500" />
          <span className="text-red-700">{error}</span>
          <button onClick={() => setError('')} className="ml-auto text-red-500">
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center space-x-2">
          <CheckCircle className="h-5 w-5 text-green-500" />
          <span className="text-green-700">{success}</span>
          <button onClick={() => setSuccess('')} className="ml-auto text-green-500">
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Authentication Section */}
      {!authState.isAuthenticated && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center space-x-2">
            <User className="h-5 w-5" />
            <span>Login to DNSE</span>
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Username</label>
              <input
                type="text"
                value={credentials.username}
                onChange={(e) => setCredentials(prev => ({ ...prev, username: e.target.value }))}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter your DNSE username"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Password</label>
              <input
                type="password"
                value={credentials.password}
                onChange={(e) => setCredentials(prev => ({ ...prev, password: e.target.value }))}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter your password"
              />
            </div>
            
            <button
              onClick={handleLogin}
              disabled={loading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </div>
        </div>
      )}

      {/* OTP Section */}
      {authState.isAuthenticated && !authState.hasTradingToken && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center space-x-2">
            <Clock className="h-5 w-5" />
            <span>Trading Authorization</span>
          </h2>
          
          <div className="space-y-4">
            <div className="flex space-x-4">
              <button
                onClick={handleRequestOTP}
                disabled={loading}
                className="flex-1 flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-orange-600 hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:opacity-50"
              >
                {loading ? 'Sending...' : 'Request OTP'}
              </button>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">OTP Code</label>
              <input
                type="text"
                value={otpCode}
                onChange={(e) => setOtpCode(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter OTP from email"
              />
            </div>
            
            <button
              onClick={handleVerifyOTP}
              disabled={loading || !otpCode}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
            >
              {loading ? 'Verifying...' : 'Verify OTP'}
            </button>
          </div>
        </div>
      )}

      {/* Main Trading Interface */}
      {authState.isAuthenticated && authState.hasTradingToken && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Account Info & Portfolio */}
          <div className="space-y-6">
            
            {/* Account Selection */}
            {accounts.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold mb-4">Account Selection</h3>
                <select
                  value={selectedAccount?.accountNo || ''}
                  onChange={(e) => {
                    const account = accounts.find(acc => acc.accountNo === e.target.value)
                    setSelectedAccount(account)
                    if (account) loadAccountData(account.accountNo)
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  {accounts.map(account => (
                    <option key={account.accountNo} value={account.accountNo}>
                      {account.accountNo} - {account.accountType || 'Trading Account'}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Buying Power */}
            {buyingPower && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
                  <DollarSign className="h-5 w-5" />
                  <span>Buying Power</span>
                </h3>
                <div className="text-2xl font-bold text-green-600">
                  {buyingPower.buyingPower?.toLocaleString()} VND
                </div>
                <p className="text-sm text-gray-600 mt-1">Available for trading</p>
              </div>
            )}

            {/* Portfolio Summary */}
            {portfolio && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
                  <Activity className="h-5 w-5" />
                  <span>Portfolio Summary</span>
                </h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Value:</span>
                    <span className="font-semibold">{portfolio.totalValue?.toLocaleString()} VND</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Cash:</span>
                    <span className="font-semibold">{portfolio.cash?.toLocaleString()} VND</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Securities:</span>
                    <span className="font-semibold">{portfolio.securitiesValue?.toLocaleString()} VND</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Order Form & Pending Orders */}
          <div className="space-y-6">
            
            {/* Order Form */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
                <Send className="h-5 w-5" />
                <span>Place Order</span>
              </h3>
              
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Symbol</label>
                    <input
                      type="text"
                      value={orderForm.symbol}
                      onChange={(e) => setOrderForm(prev => ({ ...prev, symbol: e.target.value.toUpperCase() }))}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="VCI"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Side</label>
                    <select
                      value={orderForm.side}
                      onChange={(e) => setOrderForm(prev => ({ ...prev, side: e.target.value }))}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="buy">Buy</option>
                      <option value="sell">Sell</option>
                    </select>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Quantity</label>
                    <input
                      type="number"
                      value={orderForm.quantity}
                      onChange={(e) => setOrderForm(prev => ({ ...prev, quantity: e.target.value }))}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="100"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Price</label>
                    <input
                      type="number"
                      value={orderForm.price}
                      onChange={(e) => setOrderForm(prev => ({ ...prev, price: e.target.value }))}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="25000"
                    />
                  </div>
                </div>
                
                <button
                  onClick={handlePlaceOrder}
                  disabled={loading}
                  className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 ${
                    orderForm.side === 'buy' 
                      ? 'bg-green-600 hover:bg-green-700 focus:ring-green-500' 
                      : 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
                  }`}
                >
                  {loading ? 'Placing...' : `Place ${orderForm.side === 'buy' ? 'Buy' : 'Sell'} Order`}
                </button>
              </div>
            </div>

            {/* Pending Orders */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold mb-4">Pending Orders</h3>
              
              {pendingOrders.length === 0 ? (
                <p className="text-gray-500 text-center py-4">No pending orders</p>
              ) : (
                <div className="space-y-2">
                  {pendingOrders.map((order, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className="font-medium">{order.symbol}</span>
                          <span className={`px-2 py-1 text-xs rounded ${
                            order.side === 'buy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {order.side?.toUpperCase()}
                          </span>
                        </div>
                        <div className="text-sm text-gray-600">
                          {order.quantity} @ {order.price?.toLocaleString()} VND
                        </div>
                      </div>
                      
                      <button
                        onClick={() => handleCancelOrder(order.orderId)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default DNSETrading
