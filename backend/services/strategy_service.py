from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

@dataclass
class StrategyResult:
    trades: list
    equity_curve: list
    metrics: Dict[str, Any]
    portfolio: Dict[str, Any]

class StrategyService:
    def __init__(self, initial_capital: float = 100_000_000):  # 100M VND default
        self.initial_capital = initial_capital
    
    def execute_strategy(self, strategy_code: str, price_data: list, parameters: Dict[str, Any]) -> StrategyResult:
        """Execute a trading strategy on historical data"""
        portfolio = {
            'cash': self.initial_capital,
            'position': 0,
            'history': []
        }
        
        trades = []
        equity_curve = [portfolio['cash']]
        
        try:
            # Create strategy function
            strategy_func = eval(f"lambda data, portfolio, parameters: ({strategy_code})(data, portfolio, parameters)")
            
            for i, bar in enumerate(price_data[1:], 1):  # Skip first bar
                market_data = {
                    'open': bar['open'],
                    'high': bar['high'],
                    'low': bar['low'],
                    'close': bar['close'],
                    'volume': bar['volume'],
                    'datetime': bar['date']
                }
                
                # Execute strategy
                signal = strategy_func(market_data, portfolio, parameters)
                if signal:
                    trade = self._process_signal(signal, bar, portfolio)
                    if trade:
                        trades.append(trade)
                        portfolio['history'].append(trade)
                
                # Update equity curve
                current_value = portfolio['cash'] + (portfolio['position'] * bar['close'])
                equity_curve.append(current_value)
        
        except Exception as e:
            raise Exception(f"Strategy execution error: {str(e)}")
        
        metrics = self._calculate_metrics(equity_curve, trades)
        return StrategyResult(trades, equity_curve, metrics, portfolio)
    
    def _process_signal(self, signal: Dict[str, Any], bar: Dict[str, Any], portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """Process a trading signal and update portfolio"""
        if signal['side'] == 'buy' and portfolio['cash'] >= signal['quantity'] * bar['close']:
            cost = signal['quantity'] * bar['close']
            portfolio['cash'] -= cost
            portfolio['position'] += signal['quantity']
            
            return {
                'date': bar['date'],
                'side': 'buy',
                'price': bar['close'],
                'quantity': signal['quantity'],
                'cost': cost,
                'reason': signal.get('reason', 'Strategy signal')
            }
            
        elif signal['side'] == 'sell' and portfolio['position'] >= signal['quantity']:
            proceeds = signal['quantity'] * bar['close']
            portfolio['cash'] += proceeds
            portfolio['position'] -= signal['quantity']
            
            return {
                'date': bar['date'],
                'side': 'sell',
                'price': bar['close'],
                'quantity': signal['quantity'],
                'proceeds': proceeds,
                'reason': signal.get('reason', 'Strategy signal')
            }
        
        return None
    
    def _calculate_metrics(self, equity_curve: list, trades: list) -> Dict[str, Any]:
        """Calculate trading performance metrics"""
        if len(equity_curve) < 2:
            return {}
        
        initial_capital = equity_curve[0]
        final_value = equity_curve[-1]
        
        # Calculate returns
        returns = np.diff(equity_curve) / equity_curve[:-1]
        
        # Risk metrics
        total_return = (final_value - initial_capital) / initial_capital
        volatility = np.std(returns) * np.sqrt(252) if len(returns) > 1 else 0
        mean_return = np.mean(returns) * 252
        sharpe_ratio = mean_return / volatility if volatility > 0 else 0
        
        # Drawdown
        underwater = pd.Series(equity_curve).expanding(min_periods=1).max() - equity_curve
        max_drawdown = max(underwater / pd.Series(equity_curve).expanding(min_periods=1).max())
        
        # Trade analysis
        winning_trades = [t for t in trades if t.get('proceeds', 0) - t['quantity'] * t['price'] > 0]
        losing_trades = [t for t in trades if t.get('proceeds', 0) - t['quantity'] * t['price'] <= 0]
        
        win_rate = len(winning_trades) / len(trades) if trades else 0
        avg_win = np.mean([t.get('proceeds', 0) - t['quantity'] * t['price'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.get('proceeds', 0) - t['quantity'] * t['price'] for t in losing_trades]) if losing_trades else 0
        
        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'volatility': volatility,
            'win_rate': win_rate,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': abs(avg_win / avg_loss) if avg_loss != 0 else 0,
            'sortino_ratio': sharpe_ratio * 1.4,  # Approximation
            'calmar_ratio': total_return / abs(max_drawdown) if max_drawdown != 0 else 0
        }
