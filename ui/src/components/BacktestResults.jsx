import React from 'react';
import Plot from 'react-plotly.js';
import { TrendingUp, TrendingDown, DollarSign, Calendar, BarChart3 } from 'lucide-react';

const BacktestResults = ({ results, isLoading }) => {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded mb-4"></div>
          <div className="grid grid-cols-2 gap-4">
            <div className="h-20 bg-gray-200 rounded"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <BarChart3 className="w-5 h-5 mr-2" />
          Backtest Results
        </h3>
        <div className="text-center text-gray-500 py-8">
          Run a backtest to see results
        </div>
      </div>
    );
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(value);
  };

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  // Prepare equity curve data
  const equityCurveData = {
    x: results.equity_curve?.dates || [],
    y: results.equity_curve?.values || [],
    type: 'scatter',
    mode: 'lines',
    name: 'Equity Curve',
    line: { color: '#3B82F6', width: 2 }
  };

  // Prepare drawdown data
  const drawdownData = {
    x: results.drawdown?.dates || [],
    y: results.drawdown?.values || [],
    type: 'scatter',
    mode: 'lines',
    name: 'Drawdown',
    line: { color: '#EF4444', width: 2 },
    fill: 'tonexty'
  };

  // Prepare trades scatter plot
  const buyTrades = results.trades?.filter(trade => trade.side === 'buy') || [];
  const sellTrades = results.trades?.filter(trade => trade.side === 'sell') || [];

  const buyTradesData = {
    x: buyTrades.map(trade => trade.date),
    y: buyTrades.map(trade => trade.price),
    type: 'scatter',
    mode: 'markers',
    name: 'Buy',
    marker: { color: '#10B981', size: 8, symbol: 'triangle-up' }
  };

  const sellTradesData = {
    x: sellTrades.map(trade => trade.date),
    y: sellTrades.map(trade => trade.price),
    type: 'scatter',
    mode: 'markers',
    name: 'Sell',
    marker: { color: '#EF4444', size: 8, symbol: 'triangle-down' }
  };

  // Performance metrics
  const metrics = results.metrics || {};

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-6 flex items-center">
        <BarChart3 className="w-5 h-5 mr-2" />
        Backtest Results
      </h3>

      {/* Performance Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Return</p>
              <p className={`text-lg font-semibold ${
                metrics.total_return >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {formatPercentage(metrics.total_return || 0)}
              </p>
            </div>
            {metrics.total_return >= 0 ? (
              <TrendingUp className="w-6 h-6 text-green-600" />
            ) : (
              <TrendingDown className="w-6 h-6 text-red-600" />
            )}
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Sharpe Ratio</p>
              <p className="text-lg font-semibold text-blue-600">
                {(metrics.sharpe_ratio || 0).toFixed(2)}
              </p>
            </div>
            <BarChart3 className="w-6 h-6 text-blue-600" />
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Max Drawdown</p>
              <p className="text-lg font-semibold text-red-600">
                {formatPercentage(metrics.max_drawdown || 0)}
              </p>
            </div>
            <TrendingDown className="w-6 h-6 text-red-600" />
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Win Rate</p>
              <p className="text-lg font-semibold text-purple-600">
                {formatPercentage(metrics.win_rate || 0)}
              </p>
            </div>
            <DollarSign className="w-6 h-6 text-purple-600" />
          </div>
        </div>
      </div>

      {/* Equity Curve Chart */}
      <div className="mb-6">
        <h4 className="text-md font-medium mb-3">Equity Curve</h4>
        <Plot
          data={[equityCurveData]}
          layout={{
            title: '',
            xaxis: { title: 'Date' },
            yaxis: { title: 'Portfolio Value' },
            height: 300,
            margin: { l: 50, r: 50, t: 20, b: 50 },
            showlegend: false
          }}
          config={{ responsive: true }}
          className="w-full"
        />
      </div>

      {/* Drawdown Chart */}
      <div className="mb-6">
        <h4 className="text-md font-medium mb-3">Drawdown</h4>
        <Plot
          data={[drawdownData]}
          layout={{
            title: '',
            xaxis: { title: 'Date' },
            yaxis: { title: 'Drawdown %' },
            height: 200,
            margin: { l: 50, r: 50, t: 20, b: 50 },
            showlegend: false
          }}
          config={{ responsive: true }}
          className="w-full"
        />
      </div>

      {/* Trades Chart */}
      {results.price_data && (
        <div className="mb-6">
          <h4 className="text-md font-medium mb-3">Price & Trades</h4>
          <Plot
            data={[
              {
                x: results.price_data.dates,
                y: results.price_data.prices,
                type: 'scatter',
                mode: 'lines',
                name: 'Price',
                line: { color: '#6B7280', width: 1 }
              },
              buyTradesData,
              sellTradesData
            ]}
            layout={{
              title: '',
              xaxis: { title: 'Date' },
              yaxis: { title: 'Price' },
              height: 300,
              margin: { l: 50, r: 50, t: 20, b: 50 }
            }}
            config={{ responsive: true }}
            className="w-full"
          />
        </div>
      )}

      {/* Detailed Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 className="text-md font-medium mb-3">Performance Metrics</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Total Trades:</span>
              <span className="font-medium">{metrics.total_trades || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Winning Trades:</span>
              <span className="font-medium">{metrics.winning_trades || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Losing Trades:</span>
              <span className="font-medium">{metrics.losing_trades || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Average Win:</span>
              <span className="font-medium text-green-600">
                {formatPercentage(metrics.avg_win || 0)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Average Loss:</span>
              <span className="font-medium text-red-600">
                {formatPercentage(metrics.avg_loss || 0)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Profit Factor:</span>
              <span className="font-medium">{(metrics.profit_factor || 0).toFixed(2)}</span>
            </div>
          </div>
        </div>

        <div>
          <h4 className="text-md font-medium mb-3">Risk Metrics</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Volatility:</span>
              <span className="font-medium">{formatPercentage(metrics.volatility || 0)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Sortino Ratio:</span>
              <span className="font-medium">{(metrics.sortino_ratio || 0).toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Calmar Ratio:</span>
              <span className="font-medium">{(metrics.calmar_ratio || 0).toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">VaR (95%):</span>
              <span className="font-medium text-red-600">
                {formatPercentage(metrics.var_95 || 0)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Beta:</span>
              <span className="font-medium">{(metrics.beta || 0).toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Alpha:</span>
              <span className="font-medium">{formatPercentage(metrics.alpha || 0)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Trade History Table */}
      {results.trades && results.trades.length > 0 && (
        <div className="mt-6">
          <h4 className="text-md font-medium mb-3">Recent Trades</h4>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-2 text-left">Date</th>
                  <th className="px-3 py-2 text-left">Side</th>
                  <th className="px-3 py-2 text-right">Price</th>
                  <th className="px-3 py-2 text-right">Quantity</th>
                  <th className="px-3 py-2 text-right">P&L</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {results.trades.slice(-10).map((trade, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-3 py-2">{trade.date}</td>
                    <td className="px-3 py-2">
                      <span className={`inline-flex px-2 py-1 text-xs rounded-full ${
                        trade.side === 'buy' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {trade.side.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-3 py-2 text-right">{formatCurrency(trade.price)}</td>
                    <td className="px-3 py-2 text-right">{trade.quantity}</td>
                    <td className={`px-3 py-2 text-right ${
                      trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {trade.pnl ? formatCurrency(trade.pnl) : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default BacktestResults;
