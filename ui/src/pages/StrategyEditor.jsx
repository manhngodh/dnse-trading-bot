import React, { useState, useRef } from 'react'
import Editor from '@monaco-editor/react'
import { 
  Play, 
  Save, 
  FolderOpen, 
  CheckCircle, 
  Settings, 
  Zap,
  BarChart3,
  AlertCircle,
  Download,
  Upload,
  Code,
  FileText
} from 'lucide-react'
import StrategyTemplates from '../components/StrategyTemplates'
import BacktestResults from '../components/BacktestResults'
import ParameterPanel from '../components/ParameterPanel'

const StrategyEditor = () => {
  const [code, setCode] = useState(`function strategy(data, portfolio, parameters) {
  // data: current market data {open, high, low, close, volume, datetime}
  // portfolio: {cash, position, history}
  // parameters: your custom parameters
  
  // Calculate indicators
  const price = data.close;
  const change = (price - data.open) / data.open;
  
  // Trading logic
  if (change < -parameters.threshold && portfolio.cash > price * parameters.positionSize) {
    return {
      side: 'buy', 
      quantity: parameters.positionSize, 
      reason: 'Oversold signal'
    };
  } else if (change > parameters.threshold && portfolio.position >= parameters.positionSize) {
    return {
      side: 'sell', 
      quantity: parameters.positionSize, 
      reason: 'Overbought signal'
    };
  }
  
  return null; // Hold
}`)

  const [parameters, setParameters] = useState({
    threshold: 0.01,
    positionSize: 100,
    stopLoss: 0.05,
    takeProfit: 0.1
  })

  const [testResults, setTestResults] = useState([])
  const [backtestResults, setBacktestResults] = useState(null)
  const [isValidating, setIsValidating] = useState(false)
  const [isTesting, setIsTesting] = useState(false)
  const [isBacktesting, setIsBacktesting] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState(null)
  const [currentTab, setCurrentTab] = useState('editor') // 'editor', 'templates', 'results'
  const editorRef = useRef(null)

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor
    
    // Configure JavaScript/TypeScript language features
    monaco.languages.typescript.javascriptDefaults.setCompilerOptions({
      target: monaco.languages.typescript.ScriptTarget.ES2015,
      allowNonTsExtensions: true
    })
  }

  const validateStrategy = async () => {
    setIsValidating(true)
    try {
      // Basic syntax validation
      new Function('data', 'portfolio', 'parameters', code)
      
      setTestResults(prev => [...prev, {
        type: 'success',
        message: '✅ Strategy code is valid! No syntax errors found.',
        timestamp: new Date().toLocaleTimeString()
      }])
    } catch (error) {
      setTestResults(prev => [...prev, {
        type: 'error',
        message: `❌ Syntax Error: ${error.message}`,
        timestamp: new Date().toLocaleTimeString()
      }])
    } finally {
      setIsValidating(false)
    }
  }

  const testStrategy = async () => {
    setIsTesting(true)
    setTestResults(prev => [...prev, {
      type: 'info',
      message: '🚀 Starting strategy validation test...',
      timestamp: new Date().toLocaleTimeString()
    }])

    try {
      // Call the strategy function with mock data to test logic
      const mockData = {
        open: 1000,
        high: 1050,
        low: 980,
        close: 1020,
        volume: 10000,
        datetime: new Date()
      }
      
      const mockPortfolio = {
        cash: 100000000,
        position: 0,
        history: []
      }
      
      const strategy = new Function('data', 'portfolio', 'parameters', 'return (' + code + ')(data, portfolio, parameters)')
      const result = strategy(mockData, mockPortfolio, parameters)
      
      setTestResults(prev => [...prev, {
        type: 'success',
        message: `✅ Strategy test completed! Result: ${JSON.stringify(result)}`,
        timestamp: new Date().toLocaleTimeString()
      }])
      
    } catch (error) {
      setTestResults(prev => [...prev, {
        type: 'error',
        message: `❌ Strategy test failed: ${error.message}`,
        timestamp: new Date().toLocaleTimeString()
      }])
    } finally {
      setIsTesting(false)
    }
  }

  const runBacktest = async () => {
    setIsBacktesting(true)
    setTestResults(prev => [...prev, {
      type: 'info',
      message: '📊 Starting backtest with real market data...',
      timestamp: new Date().toLocaleTimeString()
    }])

    try {
      // Try real data backtest first
      const response = await fetch('/api/backtest/real', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          strategy_code: code,
          parameters: parameters,
          symbol: parameters.symbol || 'VCI',
          start_date: parameters.startDate || '2024-01-01',
          end_date: parameters.endDate || new Date().toISOString().split('T')[0]
        })
      })

      if (response.ok) {
        const results = await response.json()
        setBacktestResults(results)
        const dataSource = results.data_source === 'vnstock_real_data' ? 'real vnstock data' : 'mock data'
        setTestResults(prev => [...prev, {
          type: 'success',
          message: `✅ Backtest completed using ${dataSource}! Total Return: ${(results.metrics.total_return * 100).toFixed(2)}%`,
          timestamp: new Date().toLocaleTimeString()
        }])
      } else {
        throw new Error('Backend API not available - using mock data')
      }
    } catch (error) {
      setTestResults(prev => [...prev, {
        type: 'warning',
        message: `⚠️ Real data unavailable, using mock data: ${error.message}`,
        timestamp: new Date().toLocaleTimeString()
      }])
      
      // Fallback to original mock backtest
      const response = await fetch('/api/backtest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          strategy_code: code,
          parameters: parameters,
          symbol: parameters.symbol || 'VN30F2412',
          start_date: parameters.startDate || '2024-01-01',
          end_date: parameters.endDate || new Date().toISOString().split('T')[0]
        })
      })

      if (response.ok) {
        const results = await response.json()
        setBacktestResults(results)
        setTestResults(prev => [...prev, {
          type: 'success',
          message: `✅ Mock backtest completed! Total Return: ${(results.metrics.total_return * 100).toFixed(2)}%`,
          timestamp: new Date().toLocaleTimeString()
        }])
      } else {
        // Generate completely local mock results if backend fails
        const mockResults = {
          metrics: {
            total_return: 0.155,
            sharpe_ratio: 1.23,
            max_drawdown: -0.082,
            win_rate: 0.625,
            total_trades: 45,
            winning_trades: 28,
            losing_trades: 17,
            avg_win: 0.035,
            avg_loss: -0.022,
            profit_factor: 2.1,
            volatility: 0.18,
            sortino_ratio: 1.67,
            calmar_ratio: 1.89,
            var_95: -0.045,
            beta: 0.85,
            alpha: 0.08
          },
          equity_curve: {
            dates: Array.from({length: 100}, (_, i) => new Date(2024, 0, i + 1).toISOString().split('T')[0]),
            values: Array.from({length: 100}, (_, i) => 100000000 * (1 + Math.random() * 0.3 - 0.15))
          },
          drawdown: {
            dates: Array.from({length: 100}, (_, i) => new Date(2024, 0, i + 1).toISOString().split('T')[0]),
            values: Array.from({length: 100}, (_, i) => Math.random() * -0.1)
          },
          trades: Array.from({length: 45}, (_, i) => ({
            date: new Date(2024, 0, i * 2 + 1).toISOString().split('T')[0],
            side: i % 2 === 0 ? 'buy' : 'sell',
            price: 1000 + Math.random() * 200,
            quantity: 100,
            pnl: Math.random() * 2000000 - 1000000
          })),
          price_data: {
            dates: Array.from({length: 100}, (_, i) => new Date(2024, 0, i + 1).toISOString().split('T')[0]),
            prices: Array.from({length: 100}, (_, i) => 1000 + Math.random() * 200)
          },
          data_source: 'local_mock'
        }

        setBacktestResults(mockResults)
        setTestResults(prev => [...prev, {
          type: 'success',
          message: `✅ Local mock backtest completed! Total Return: ${(mockResults.metrics.total_return * 100).toFixed(2)}%`,
          timestamp: new Date().toLocaleTimeString()
        }])
      }
    } finally {
      setIsBacktesting(false)
    }
    }

  const saveStrategy = async () => {
    try {
      const strategyData = {
        code,
        parameters,
        timestamp: new Date().toISOString()
      }
      
      // In real implementation, save to backend
      localStorage.setItem('dnse_strategy', JSON.stringify(strategyData))
      
      setTestResults(prev => [...prev, {
        type: 'success',
        message: '💾 Strategy saved successfully!',
        timestamp: new Date().toLocaleTimeString()
      }])
    } catch (error) {
      setTestResults(prev => [...prev, {
        type: 'error',
        message: `❌ Save failed: ${error.message}`,
        timestamp: new Date().toLocaleTimeString()
      }])
    }
  }

  const loadStrategy = async () => {
    try {
      const saved = localStorage.getItem('dnse_strategy')
      if (saved) {
        const strategyData = JSON.parse(saved)
        setCode(strategyData.code)
        setParameters(strategyData.parameters || parameters)
        
        setTestResults(prev => [...prev, {
          type: 'success',
          message: '📂 Strategy loaded successfully!',
          timestamp: new Date().toLocaleTimeString()
        }])
      } else {
        setTestResults(prev => [...prev, {
          type: 'info',
          message: '📂 No saved strategy found.',
          timestamp: new Date().toLocaleTimeString()
        }])
      }
    } catch (error) {
      setTestResults(prev => [...prev, {
        type: 'error',
        message: `❌ Load failed: ${error.message}`,
        timestamp: new Date().toLocaleTimeString()
      }])
    }
  }

  const exportStrategy = () => {
    const strategyData = {
      code,
      parameters,
      name: 'Custom Strategy',
      version: '1.0.0',
      created: new Date().toISOString()
    }
    
    const blob = new Blob([JSON.stringify(strategyData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'strategy.json'
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleTemplateSelect = (template) => {
    setSelectedTemplate(template)
    setCode(template.code)
    setParameters(prev => ({
      ...prev,
      ...Object.fromEntries(
        Object.entries(template.params).map(([key, config]) => [key, config.default])
      )
    }))
    
    setTestResults(prev => [...prev, {
      type: 'success',
      message: `📋 Template "${template.name}" loaded successfully!`,
      timestamp: new Date().toLocaleTimeString()
    }])
  }

  const handleParametersChange = (newParams) => {
    setParameters(newParams)
  }

  const handleParametersSave = (params) => {
    setParameters(params)
    setTestResults(prev => [...prev, {
      type: 'success',
      message: '⚙️ Parameters updated successfully!',
      timestamp: new Date().toLocaleTimeString()
    }])
  }

  const handleParametersReset = () => {
    if (selectedTemplate) {
      const defaultParams = Object.fromEntries(
        Object.entries(selectedTemplate.params).map(([key, config]) => [key, config.default])
      )
      setParameters(prev => ({
        ...prev,
        ...defaultParams
      }))
    }
  }

  const importStrategy = (event) => {
    const file = event.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const strategyData = JSON.parse(e.target.result)
          setCode(strategyData.code)
          setParameters(strategyData.parameters || parameters)
          
          setTestResults(prev => [...prev, {
            type: 'success',
            message: '📥 Strategy imported successfully!',
            timestamp: new Date().toLocaleTimeString()
          }])
        } catch (error) {
          setTestResults(prev => [...prev, {
            type: 'error',
            message: `❌ Import failed: Invalid file format`,
            timestamp: new Date().toLocaleTimeString()
          }])
        }
      }
      reader.readAsText(file)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <Settings className="h-6 w-6 mr-2 text-blue-600" />
              Strategy Editor & Backtester
            </h1>
            <p className="text-gray-600">Write, test, and optimize your DNSE trading strategies</p>
          </div>
          
          <div className="flex space-x-2">
            <input
              type="file"
              accept=".json"
              onChange={importStrategy}
              className="hidden"
              id="import-strategy"
            />
            <label 
              htmlFor="import-strategy" 
              className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 transition-colors flex items-center cursor-pointer"
            >
              <Upload className="h-4 w-4 mr-2" />
              Import
            </label>
            <button 
              onClick={exportStrategy} 
              className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 transition-colors flex items-center"
            >
              <Download className="h-4 w-4 mr-2" />
              Export
            </button>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            <button
              onClick={() => setCurrentTab('templates')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                currentTab === 'templates'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Strategy Templates
            </button>
            <button
              onClick={() => setCurrentTab('editor')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                currentTab === 'editor'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Code Editor
            </button>
            <button
              onClick={() => setCurrentTab('results')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                currentTab === 'results'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Backtest Results
            </button>
          </nav>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Main Content Area */}
        <div className="xl:col-span-2 space-y-6">
          {/* Strategy Templates */}
          {currentTab === 'templates' && (
            <StrategyTemplates onSelectTemplate={handleTemplateSelect} />
          )}

          {/* Code Editor */}
          {currentTab === 'editor' && (
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Strategy Code</h3>
                <div className="flex space-x-2">
                  <button 
                    onClick={validateStrategy}
                    disabled={isValidating}
                    className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                      isValidating 
                        ? 'bg-gray-400 text-white cursor-not-allowed'
                        : 'bg-green-500 text-white hover:bg-green-600'
                    }`}
                  >
                    <CheckCircle className="h-4 w-4 mr-1 inline" />
                    {isValidating ? 'Validating...' : 'Validate'}
                  </button>
                  <button 
                    onClick={testStrategy}
                    disabled={isTesting}
                    className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                      isTesting 
                        ? 'bg-gray-400 text-white cursor-not-allowed'
                        : 'bg-blue-500 text-white hover:bg-blue-600'
                    }`}
                  >
                    <Play className="h-4 w-4 mr-1 inline" />
                    {isTesting ? 'Testing...' : 'Quick Test'}
                  </button>
                  <button 
                    onClick={runBacktest}
                    disabled={isBacktesting}
                    className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                      isBacktesting 
                        ? 'bg-gray-400 text-white cursor-not-allowed'
                        : 'bg-purple-500 text-white hover:bg-purple-600'
                    }`}
                  >
                    <BarChart3 className="h-4 w-4 mr-1 inline" />
                    {isBacktesting ? 'Running...' : 'Full Backtest'}
                  </button>
                  <button 
                    onClick={saveStrategy} 
                    className="bg-yellow-500 text-white px-4 py-2 rounded text-sm hover:bg-yellow-600 transition-colors"
                  >
                    <Save className="h-4 w-4 mr-1 inline" />
                    Save
                  </button>
                  <button 
                    onClick={loadStrategy} 
                    className="bg-gray-500 text-white px-4 py-2 rounded text-sm hover:bg-gray-600 transition-colors"
                  >
                    <FolderOpen className="h-4 w-4 mr-1 inline" />
                    Load
                  </button>
                </div>
              </div>
              
              <div className="border border-gray-300 rounded-lg overflow-hidden">
                <Editor
                  height="500px"
                  defaultLanguage="javascript"
                  value={code}
                  onChange={setCode}
                  onMount={handleEditorDidMount}
                  theme="vs-light"
                  options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    lineNumbers: 'on',
                    scrollBeyondLastLine: false,
                    automaticLayout: true,
                    tabSize: 2,
                    wordWrap: 'on',
                    folding: true,
                    lineNumbersMinChars: 3
                  }}
                />
              </div>
            </div>
          )}

          {/* Backtest Results */}
          {currentTab === 'results' && (
            <BacktestResults results={backtestResults} isLoading={isBacktesting} />
          )}

          {/* Test Results Console */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Console Output</h3>
            <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm max-h-64 overflow-y-auto">
              {testResults.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <AlertCircle className="h-8 w-8 mx-auto mb-2" />
                  <p>No output yet. Run validation or tests to see results.</p>
                </div>
              ) : (
                testResults.map((result, index) => (
                  <div key={index} className="mb-2">
                    <span className="text-gray-400">[{result.timestamp}]</span> {result.message}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Sidebar - Parameter Panel */}
        <div className="xl:col-span-1">
          <ParameterPanel 
            strategy={selectedTemplate}
            onParametersChange={handleParametersChange}
            onSave={handleParametersSave}
            onReset={handleParametersReset}
          />
        </div>
      </div>
    </div>
  )
}

export default StrategyEditor
