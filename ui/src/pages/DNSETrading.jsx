import React, { useState, useEffect } from 'react'
import { User, RefreshCw } from 'lucide-react'

// Auth Components
import DNSEAuth from '../components/auth/DNSEAuth'
import LoginForm from '../components/auth/LoginForm'

// Trading Components
import AccountSelection from '../components/trading/AccountSelection'
import BuyingPower from '../components/trading/BuyingPower'
import PortfolioSummary from '../components/trading/PortfolioSummary'
import OrderForm from '../components/trading/OrderForm'
import PendingOrders from '../components/trading/PendingOrders'

// Common Components
import Alert from '../components/common/Alert'

const DNSETrading = () => {
  // Unified authentication state
  const [authState, setAuthState] = useState({
    isAuthenticated: false,
    hasJWT: false,
    hasTradingToken: false,
    investorInfo: null,
    tradingToken: null
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

  // Check auth status when component mounts
  useEffect(() => {
    console.log('Checking DNSE authentication status...', authState.isAuthenticated, loading)
    if (!authState.isAuthenticated && !loading) {
      setLoading(true);
      checkDNSEStatus()
        .finally(() => setLoading(false));
    }
  }, [])

  // Handle authentication changes from DNSEAuth component
  const handleAuthChange = async (data) => {
    try {
      // Update unified auth state
      setAuthState(prev => ({
        ...prev,
        isAuthenticated: data.isAuthenticated,
        hasTradingToken: data.hasTradingToken,
        investorInfo: data.userInfo,
        tradingToken: data.tradingToken
      }))
      
      // Pass auth data to parent component if onAuthChange prop exists
      if (onAuthChange) {
        onAuthChange(data)
      }

      // If authenticated, load accounts
      if (data.isAuthenticated) {
        await loadAccounts()
      }
    } catch (error) {
      console.error('Error in handleAuthChange:', error)
      setError('Failed to complete authentication process')
    }
  }

  const checkDNSEStatus = async () => {
    try {
      const response = await fetch('/api/dnse/status')
      const data = await response.json()
      console.log('DNSE status response:', data.authenticated)
      setAuthState(prev => ({
        ...prev,
        isAuthenticated: data.authenticated,
        hasJWT: data.authenticated,
        hasTradingToken: data.has_trading_token,
      }))
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
      console.log('Login response:', data)
      
      // Check if we have an access token, which indicates success
      if (data.access_token) {
        // Extract user info from JWT token if possible
        let investorInfo = null
        try {
          // JWT tokens have three parts separated by dots
          const tokenParts = data.access_token.split('.');
          if (tokenParts.length === 3) {
            // Decode the middle part (payload)
            const payload = JSON.parse(atob(tokenParts[1]));
            investorInfo = {
              fullName: payload.fullName || '',
              email: payload.customerEmail || '',
              mobile: payload.customerMobile || '',
              customerId: payload.customerId || '',
              userId: payload.userId || ''
            };
          }
        } catch (error) {
          console.error('Error parsing JWT token:', error);
        }
        
        setAuthState({
          isAuthenticated: true,
          hasJWT: true,
          hasTradingToken: !data.requires_otp, // If requires_otp is true, we don't have trading token yet
          investorInfo: investorInfo,
          sessionId: data.session_id
        })
        
        // Store token for subsequent requests
        localStorage.setItem('dnse_access_token', data.access_token);
        
        setSuccess('Login successful!')
        console.log('Investor Info:', authState)
        loadAccounts()
      } else if (data.error) {
        setError(data.error)
      } else {
        setError('Login failed: Invalid response from server')
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
      setLoading(true)
      setError('')
      const response = await fetch('/api/dnse/accounts')
      const data = await response.json()
      
      if (data.success) {
        setAccounts(data.accounts)
        if (data.accounts.length > 0) {
          setSelectedAccount(data.accounts[0])
          await loadAccountData(data.accounts[0].accountNo)
        } else {
          setError('No trading accounts found')
        }
      } else {
        setError(data.error || 'Failed to load accounts')
      }
    } catch (error) {
      console.error('Error loading accounts:', error)
      setError('Network error while loading accounts')
    } finally {
      setLoading(false)
    }
  }

  const loadAccountData = async (accountNo) => {
    if (!accountNo) {
      console.error('No account number provided to loadAccountData')
      return
    }

    setLoading(true)
    setError('')
    
    try {
      // Load portfolio
      const portfolioResponse = await fetch(`/api/dnse/portfolio/${accountNo}`)
      const portfolioData = await portfolioResponse.json()
      if (portfolioData.success) {
        setPortfolio(portfolioData.portfolio)
      } else {
        console.error('Failed to load portfolio:', portfolioData.error)
      }

      // Load buying power
      const buyingPowerResponse = await fetch(`/api/dnse/buying-power/${accountNo}`)
      const buyingPowerData = await buyingPowerResponse.json()
      if (buyingPowerData.success) {
        setBuyingPower(buyingPowerData.buying_power)
      } else {
        console.error('Failed to load buying power:', buyingPowerData.error)
      }

      // Load pending orders
      const ordersResponse = await fetch(`/api/dnse/pending-orders/${accountNo}`)
      const ordersData = await ordersResponse.json()
      if (ordersData.success) {
        setPendingOrders(ordersData.orders)
      } else {
        console.error('Failed to load pending orders:', ordersData.error)
      }
    } catch (error) {
      console.error('Error loading account data:', error)
      setError('Failed to load account information')
    } finally {
      setLoading(false)
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
      <Alert type="error" message={error} onClose={() => setError('')} />
      <Alert type="success" message={success} onClose={() => setSuccess('')} />

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

      {/* Main Trading Interface */}
      {authState.isAuthenticated && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Account Info & Portfolio */}
          <div className="space-y-6">
            <AccountSelection
              accounts={accounts}
              selectedAccount={selectedAccount}
              onAccountChange={(account) => {
                setSelectedAccount(account);
                if (account) loadAccountData(account.accountNo);
              }}
            />
            <BuyingPower buyingPower={buyingPower} />
            <PortfolioSummary portfolio={portfolio} />
          </div>

          {/* Order Form & Pending Orders */}
          <div className="space-y-6">
            <OrderForm
              formData={orderForm}
              onChange={setOrderForm}
              onSubmit={handlePlaceOrder}
              loading={loading}
            />
            <PendingOrders
              orders={pendingOrders}
              onCancelOrder={handleCancelOrder}
            />
          </div>
        </div>
      )}
    </div>
  )
}

export default DNSETrading
