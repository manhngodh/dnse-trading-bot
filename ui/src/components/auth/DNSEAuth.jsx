import React, { useState, useEffect } from 'react'
import { Shield, Mail, Key, User, CheckCircle, XCircle, RefreshCw, LogOut } from 'lucide-react'

const DNSEAuth = ({ onAuthChange }) => {
  const [authState, setAuthState] = useState({
    step: 'login', // 'login', 'otp', 'success'
    isLoading: false,
    isAuthenticated: false,
    hasTradingToken: false,
    userInfo: null,
    accounts: []
  })

  const [formData, setFormData] = useState({
    username: '',
    password: '',
    otpCode: ''
  })

  const [alert, setAlert] = useState(null)

  const API_BASE = 'http://localhost:8000/api'

  useEffect(() => {
    checkAuthStatus()
  }, [])

  useEffect(() => {
    if (onAuthChange) {
      onAuthChange({
        isAuthenticated: authState.isAuthenticated,
        hasTradingToken: authState.hasTradingToken,
        userInfo: authState.userInfo,
        tradingToken: authState.tradingToken,
        accounts: authState.accounts
      })
    }
  }, [authState.isAuthenticated, authState.hasTradingToken, authState.userInfo, authState.tradingToken, authState.accounts, onAuthChange])

  const showAlert = (message, type = 'info') => {
    setAlert({ message, type })
    setTimeout(() => setAlert(null), 5000)
  }

  const checkAuthStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/auth/status`, {
        credentials: 'include'
      })
      const data = await response.json()

      if (data.authenticated && data.has_trading_token) {
        setAuthState(prev => ({
          ...prev,
          step: 'success',
          isAuthenticated: true,
          hasTradingToken: true,
          tradingToken: data.trading_token || null
        }))
        loadUserInfo()
      } else if (data.authenticated) {
        setAuthState(prev => ({
          ...prev,
          step: 'loggedin', // Stay logged in, allow OTP request for trading
          isAuthenticated: true,
          hasTradingToken: false,
          tradingToken: null
        }))
        loadUserInfo()
      } else {
        setAuthState(prev => ({
          ...prev,
          step: 'login',
          isAuthenticated: false,
          hasTradingToken: false
        }))
      }
    } catch (error) {
      console.error('Error checking auth status:', error)
      setAuthState(prev => ({
        ...prev,
        step: 'login',
        isAuthenticated: false,
        hasTradingToken: false
      }))
    }
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    
    if (!formData.username || !formData.password) {
      showAlert('Please enter both username and password', 'error')
      return
    }

    setAuthState(prev => ({ ...prev, isLoading: true }))

    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          username: formData.username,
          password: formData.password
        })
      })

      const data = await response.json()

      if (data.success) {
        showAlert('Login successful! You are now logged in.', 'success')
        setAuthState(prev => ({
          ...prev,
          step: 'loggedin', // New step for logged-in, not trading
          isAuthenticated: true
        }))
        // Do NOT call requestOTP() automatically
      } else {
        showAlert(data.error || 'Login failed', 'error')
      }
    } catch (error) {
      showAlert('Network error. Please try again.', 'error')
      console.error('Login error:', error)
    } finally {
      setAuthState(prev => ({ ...prev, isLoading: false }))
    }
  }

  const requestOTP = async () => {
    setAuthState(prev => ({ ...prev, isLoading: true }))

    try {
      const response = await fetch(`${API_BASE}/auth/request-otp`, {
        method: 'POST',
        credentials: 'include'
      })

      const data = await response.json()

      if (data.success) {
        showAlert('OTP sent to your email successfully!', 'success')
      } else {
        showAlert(data.error || 'Failed to send OTP', 'error')
      }
    } catch (error) {
      showAlert('Network error. Please try again.', 'error')
      console.error('OTP request error:', error)
    } finally {
      setAuthState(prev => ({ ...prev, isLoading: false }))
    }
  }

  const handleVerifyOTP = async (e) => {
    e.preventDefault()

    if (!formData.otpCode || formData.otpCode.length !== 6) {
      showAlert('Please enter a valid 6-digit OTP code', 'error')
      return
    }

    setAuthState(prev => ({ ...prev, isLoading: true }))

    try {
      const response = await fetch(`${API_BASE}/auth/verify-otp`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ otp_code: formData.otpCode })
      })

      const data = await response.json()

      if (data.success) {
        showAlert('OTP verified successfully! Trading access granted.', 'success')
        setAuthState(prev => ({
          ...prev,
          step: 'success',
          hasTradingToken: true,
          userInfo: data.user_info,
          tradingToken: data.trading_token || null,
          accounts: data.accounts || []
        }))
      } else {
        showAlert(data.error || 'OTP verification failed', 'error')
      }
    } catch (error) {
      showAlert('Network error. Please try again.', 'error')
      console.error('OTP verification error:', error)
    } finally {
      setAuthState(prev => ({ ...prev, isLoading: false }))
    }
  }

  const loadUserInfo = async () => {
    try {
      const response = await fetch(`${API_BASE}/auth/user-info`, {
        credentials: 'include'
      })

      const data = await response.json()

      if (data.success) {
        setAuthState(prev => ({
          ...prev,
          userInfo: data.user_info,
          accounts: data.accounts || []
        }))
      }
    } catch (error) {
      console.error('Error loading user info:', error)
    }
  }

  const handleLogout = async () => {
    setAuthState(prev => ({ ...prev, isLoading: true }))

    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        credentials: 'include'
      })

      showAlert('Logged out successfully', 'success')
      setAuthState({
        step: 'login',
        isLoading: false,
        isAuthenticated: false,
        hasTradingToken: false,
        userInfo: null,
        accounts: []
      })
      setFormData({ username: '', password: '', otpCode: '' })
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setAuthState(prev => ({ ...prev, isLoading: false }))
    }
  }

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const renderAlert = () => {
    if (!alert) return null

    const alertStyles = {
      success: 'bg-green-50 border-green-200 text-green-800',
      error: 'bg-red-50 border-red-200 text-red-800',
      info: 'bg-blue-50 border-blue-200 text-blue-800'
    }

    const alertIcons = {
      success: CheckCircle,
      error: XCircle,
      info: Shield
    }

    const Icon = alertIcons[alert.type]

    return (
      <div className={`border rounded-lg p-3 mb-4 flex items-center space-x-2 ${alertStyles[alert.type]}`}>
        <Icon className="h-4 w-4 flex-shrink-0" />
        <span className="text-sm">{alert.message}</span>
      </div>
    )
  }

  const renderLoginStep = () => (
    <div className="space-y-4">
      <div className="text-center mb-6">
        <Shield className="h-12 w-12 text-blue-600 mx-auto mb-3" />
        <h2 className="text-xl font-bold text-gray-900">DNSE Authentication</h2>
        <p className="text-sm text-gray-600">Secure login to DNSE trading platform</p>
      </div>

      <form onSubmit={handleLogin} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Username
          </label>
          <div className="relative">
            <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              value={formData.username}
              onChange={(e) => handleInputChange('username', e.target.value)}
              className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter your username"
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Password
          </label>
          <div className="relative">
            <Key className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="password"
              value={formData.password}
              onChange={(e) => handleInputChange('password', e.target.value)}
              className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter your password"
              required
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={authState.isLoading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          {authState.isLoading ? (
            <>
              <RefreshCw className="h-4 w-4 animate-spin" />
              <span>Logging in...</span>
            </>
          ) : (
            <span>Login to DNSE</span>
          )}
        </button>
      </form>
    </div>
  )

  const renderLoggedInStep = () => (
    <div className="space-y-4">
      <div className="text-center mb-6">
        <Shield className="h-12 w-12 text-blue-600 mx-auto mb-3" />
        <h2 className="text-xl font-bold text-gray-900">Welcome to DNSE</h2>
        <p className="text-sm text-gray-600">You are logged in. To enable trading, request and verify OTP.</p>
      </div>

      <button
        type="button"
        onClick={() => setAuthState(prev => ({ ...prev, step: 'otp' }))}
        disabled={authState.isLoading}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
      >
        <Mail className="h-4 w-4" />
        <span>Request OTP for Trading</span>
      </button>

      <button
        onClick={handleLogout}
        disabled={authState.isLoading}
        className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
      >
        <LogOut className="h-4 w-4" />
        <span>Logout</span>
      </button>
    </div>
  )

  const renderOTPStep = () => (
    <div className="space-y-4">
      <div className="text-center mb-6">
        <Mail className="h-12 w-12 text-blue-600 mx-auto mb-3" />
        <h2 className="text-xl font-bold text-gray-900">OTP Verification</h2>
        <p className="text-sm text-gray-600">Please check your email for the verification code</p>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
        <p className="text-sm text-blue-800">
          <strong>OTP Required:</strong> An email with your verification code has been sent.
        </p>
      </div>

      <form onSubmit={handleVerifyOTP} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Enter OTP Code
          </label>
          <input
            type="text"
            value={formData.otpCode}
            onChange={(e) => handleInputChange('otpCode', e.target.value.replace(/\D/g, ''))}
            maxLength={6}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-center text-lg tracking-widest"
            placeholder="000000"
            required
          />
        </div>

        <button
          type="submit"
          disabled={authState.isLoading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          {authState.isLoading ? (
            <>
              <RefreshCw className="h-4 w-4 animate-spin" />
              <span>Verifying...</span>
            </>
          ) : (
            <span>Verify OTP</span>
          )}
        </button>

        <button
          type="button"
          onClick={requestOTP}
          disabled={authState.isLoading}
          className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Resend OTP
        </button>
      </form>
    </div>
  )

  const renderSuccessStep = () => (
    <div className="space-y-4">
      <div className="text-center mb-6">
        <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-3" />
        <h2 className="text-xl font-bold text-gray-900">Authentication Successful</h2>
        <p className="text-sm text-gray-600">You now have full trading access</p>
      </div>

      <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4 flex items-center space-x-2">
        <CheckCircle className="h-4 w-4 text-green-600 flex-shrink-0" />
        <span className="text-sm text-green-800">
          <strong>Trading Session Active:</strong> Full access granted
        </span>
      </div>

      {authState.userInfo && (
        <div className="bg-gray-50 rounded-lg p-4 space-y-3">
          <h3 className="font-semibold text-gray-900">User Information</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Username:</span>
              <span className="font-medium">{authState.userInfo.username || 'N/A'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Full Name:</span>
              <span className="font-medium">{authState.userInfo.fullName || 'N/A'}</span>
            </div>
          </div>

          {authState.accounts.length > 0 && (
            <>
              <h4 className="font-semibold text-gray-900 mt-4">Trading Accounts</h4>
              <div className="space-y-2">
                {authState.accounts.map((account, index) => (
                  <div key={index} className="bg-white p-3 rounded border">
                    <div className="font-medium text-sm">{account.accountName || 'Trading Account'}</div>
                    <div className="text-xs text-gray-500 font-mono">{account.accountNo || account.accountId || 'N/A'}</div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      <button
        onClick={handleLogout}
        disabled={authState.isLoading}
        className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
      >
        <LogOut className="h-4 w-4" />
        <span>Logout</span>
      </button>
    </div>
  )

  return (
    <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
      {renderAlert()}
      {authState.isLoading && (
        <div className="flex items-center justify-center space-x-2 mb-4 text-blue-600">
          <RefreshCw className="h-4 w-4 animate-spin" />
          <span className="text-sm">Processing...</span>
        </div>
      )}
      {authState.step === 'login' && renderLoginStep()}
      {authState.step === 'loggedin' && renderLoggedInStep()}
      {authState.step === 'otp' && renderOTPStep()}
      {authState.step === 'success' && renderSuccessStep()}
    </div>
  )
}

export default DNSEAuth
