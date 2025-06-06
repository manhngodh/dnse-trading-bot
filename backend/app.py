from flask import Flask, g, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime, timedelta
import random
import math
import pandas as pd
from vnstock import Vnstock
import traceback

from core.config import active_config
from core.logging import setup_logging
from routes.auth import auth_bp
from routes.market import market_bp
from routes.order import order_bp
from routes.portfolio import portfolio_bp
from channels.mqtt_channel import mqtt_channel

# Initialize logging
logger = setup_logging()

# Add the project root to Python path to import DNSE client
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Import UI DNSE Client
try:
    from ui_dnse_client import UIDNSEClient
    UI_DNSE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: UI DNSE client not available: {e}")
    UI_DNSE_AVAILABLE = False

try:
    from src.clients.dnse_client import DNSEClient
    from src.clients.demo_client import DemoTradingClient
    from src.core.data_structures import OrderRequest, OrderSide, OrderType
    from src.core.exceptions import DNSEAPIError, TradingBotError
    DNSE_AVAILABLE = True
    DEMO_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Trading clients not available: {e}")
    DNSE_AVAILABLE = False
    DEMO_AVAILABLE = False
    # Create mock classes to prevent errors
    class DNSEClient:
        pass
    class DemoTradingClient:
        pass
    class OrderRequest:
        pass
    class OrderSide:
        BUY = "BUY"
        SELL = "SELL"
    class OrderType:
        LIMIT = "LIMIT"
        MARKET = "MARKET"
    class DNSEAPIError(Exception):
        pass
    class TradingBotError(Exception):
        pass

app = Flask(__name__)
CORS(app)

# Global trading client instances
dnse_client = None
demo_client = None
active_client_type = None  # 'dnse' or 'demo'

# Initialize UI DNSE client if available
if UI_DNSE_AVAILABLE:
    ui_client = UIDNSEClient()
else:
    ui_client = None

# Mock data generator for backtesting
def generate_mock_price_data(symbol='VN30F2412', days=100):
    """Generate mock OHLCV data for backtesting"""
    base_date = datetime.now() - timedelta(days=days)
    
    data = []
    current_price = 1000
    
    for i in range(days):
        date = base_date + timedelta(days=i)
        
        # Generate realistic price movements
        change = random.gauss(0, 0.02)  # 2% daily volatility
        current_price *= (1 + change)
        
        high = current_price * (1 + abs(random.gauss(0, 0.01)))
        low = current_price * (1 - abs(random.gauss(0, 0.01)))
        open_price = current_price * (1 + random.gauss(0, 0.005))
        volume = int(random.uniform(10000, 50000))
        
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(current_price, 2),
            'volume': volume
        })
    
    return data

def execute_strategy(strategy_code, price_data, parameters):
    """Execute a trading strategy on historical data"""
    
    # Initialize portfolio
    portfolio = {
        'cash': 100000000,  # 100M VND starting capital
        'position': 0,
        'history': []
    }
    
    trades = []
    equity_curve = [portfolio['cash']]
    
    try:
        # Create strategy function
        strategy_func = eval(f"lambda data, portfolio, parameters: ({strategy_code})(data, portfolio, parameters)")
        
        for i, bar in enumerate(price_data[1:], 1):  # Skip first bar
            # Convert bar to expected format
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
                if signal['side'] == 'buy' and portfolio['cash'] >= signal['quantity'] * bar['close']:
                    # Execute buy order
                    cost = signal['quantity'] * bar['close']
                    portfolio['cash'] -= cost
                    portfolio['position'] += signal['quantity']
                    
                    trade = {
                        'date': bar['date'],
                        'side': 'buy',
                        'price': bar['close'],
                        'quantity': signal['quantity'],
                        'cost': cost,
                        'reason': signal.get('reason', 'Strategy signal')
                    }
                    trades.append(trade)
                    portfolio['history'].append(trade)
                    
                elif signal['side'] == 'sell' and portfolio['position'] >= signal['quantity']:
                    # Execute sell order
                    proceeds = signal['quantity'] * bar['close']
                    portfolio['cash'] += proceeds
                    portfolio['position'] -= signal['quantity']
                    
                    trade = {
                        'date': bar['date'],
                        'side': 'sell',
                        'price': bar['close'],
                        'quantity': signal['quantity'],
                        'proceeds': proceeds,
                        'reason': signal.get('reason', 'Strategy signal')
                    }
                    trades.append(trade)
                    portfolio['history'].append(trade)
            
            # Calculate current portfolio value
            current_value = portfolio['cash'] + (portfolio['position'] * bar['close'])
            equity_curve.append(current_value)
    
    except Exception as e:
        raise Exception(f"Strategy execution error: {str(e)}")
    
    return trades, equity_curve

def calculate_std(values):
    """Calculate standard deviation"""
    if len(values) < 2:
        return 0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)

def calculate_mean(values):
    """Calculate mean"""
    return sum(values) / len(values) if values else 0

def calculate_metrics(equity_curve, trades):
    """Calculate trading performance metrics"""
    
    if len(equity_curve) < 2:
        return {}
    
    initial_capital = equity_curve[0]
    final_value = equity_curve[-1]
    
    # Basic metrics
    total_return = (final_value - initial_capital) / initial_capital
    
    # Calculate returns
    returns = []
    for i in range(1, len(equity_curve)):
        if equity_curve[i-1] != 0:
            returns.append((equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1])
    
    # Risk metrics
    volatility = calculate_std(returns) * math.sqrt(252) if len(returns) > 1 else 0
    mean_return = calculate_mean(returns) * 252
    sharpe_ratio = mean_return / volatility if volatility > 0 else 0
    
    # Drawdown calculation
    peak = 0
    max_drawdown = 0
    for value in equity_curve:
        if value > peak:
            peak = value
        drawdown = (value - peak) / peak if peak > 0 else 0
        if drawdown < max_drawdown:
            max_drawdown = drawdown
    
    # Trade analysis
    winning_trades = []
    losing_trades = []
    
    # Calculate P&L for trades
    pnl_trades = []
    
    for trade in trades:
        if trade['side'] == 'sell':
            # Simple P&L calculation
            pnl = trade.get('proceeds', 0) - trade['quantity'] * trade['price']
            pnl_trades.append(pnl)
            if pnl > 0:
                winning_trades.append(trade)
            else:
                losing_trades.append(trade)
    
    win_rate = len(winning_trades) / len(trades) if trades else 0
    avg_win = calculate_mean([pnl for pnl in pnl_trades if pnl > 0])
    avg_loss = calculate_mean([pnl for pnl in pnl_trades if pnl < 0])
    profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
    
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
        'profit_factor': profit_factor,
        'sortino_ratio': sharpe_ratio * 1.4,  # Approximation
        'calmar_ratio': total_return / abs(max_drawdown) if max_drawdown != 0 else 0,
        'var_95': sorted(returns)[int(len(returns) * 0.05)] if len(returns) > 0 else 0,
        'beta': 0.85,  # Mock value
        'alpha': total_return - 0.05  # Mock risk-free rate
    }

# Real market data functions using vnstock
def get_real_market_data(symbol='VCI', start_date=None, end_date=None, interval='1D'):
    """Get real market data from vnstock"""
    try:
        stock = Vnstock().stock(symbol=symbol, source='VCI')
        
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        # Get historical data
        df = stock.quote.history(start=start_date, end=end_date, interval=interval)
        
        # Convert to list of dictionaries
        data = []
        for index, row in df.iterrows():
            data.append({
                'date': index.strftime('%Y-%m-%d') if hasattr(index, 'strftime') else str(index),
                'open': float(row.get('open', 0)),
                'high': float(row.get('high', 0)),
                'low': float(row.get('low', 0)),
                'close': float(row.get('close', 0)),
                'volume': int(row.get('volume', 0))
            })
        
        return data
    except Exception as e:
        print(f"Error fetching real data for {symbol}: {str(e)}")
        traceback.print_exc()
        # Fallback to mock data
        return generate_mock_price_data(symbol, 30)

def get_current_quote(symbol='VCI'):
    """Get current market quote"""
    try:
        stock = Vnstock().stock(symbol=symbol, source='VCI')
        quote = stock.quote.overview()
        
        if isinstance(quote, pd.DataFrame) and not quote.empty:
            row = quote.iloc[0]
            return {
                'symbol': symbol,
                'price': float(row.get('price', 0)),
                'change': float(row.get('change', 0)),
                'change_percent': float(row.get('change_percent', 0)),
                'volume': int(row.get('volume', 0)),
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'symbol': symbol,
                'price': 1000 + random.uniform(-50, 50),
                'change': random.uniform(-20, 20),
                'change_percent': random.uniform(-2, 2),
                'volume': random.randint(10000, 100000),
                'timestamp': datetime.now().isoformat()
            }
    except Exception as e:
        print(f"Error fetching quote for {symbol}: {str(e)}")
        # Return mock data
        return {
            'symbol': symbol,
            'price': 1000 + random.uniform(-50, 50),
            'change': random.uniform(-20, 20),
            'change_percent': random.uniform(-2, 2),
            'volume': random.randint(10000, 100000),
            'timestamp': datetime.now().isoformat()
        }

def get_market_overview():
    """Get market overview with multiple symbols"""
    symbols = ['VCI', 'VCB', 'HPG', 'MSN', 'TCB', 'VIC', 'FPT', 'VHM', 'POW', 'ACB']
    overview = []
    
    for symbol in symbols[:5]:  # Limit to 5 symbols to avoid rate limiting
        try:
            quote = get_current_quote(symbol)
            overview.append(quote)
        except Exception as e:
            print(f"Error fetching overview for {symbol}: {str(e)}")
            continue
    
    return overview

# =============================================================================
# DNSE Trading API Endpoints
# =============================================================================

@app.route('/api/dnse/login', methods=['POST'])
def dnse_login():
    """Login to DNSE using UI client"""
    global dnse_client, active_client_type
    
    if not UI_DNSE_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'DNSE UI client not available. Check installation and dependencies.',
            'error_type': 'SYSTEM_ERROR',
            'user_message': 'Trading service is not available'
        }), 400
    
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Use UI client for login
        result = ui_client.login(username, password)
        
        if result['success']:
            active_client_type = 'dnse'
            dnse_client = ui_client.core_client  # Keep reference for compatibility
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'UNEXPECTED_ERROR',
            'user_message': 'An unexpected error occurred during login'
        }), 500

@app.route('/api/dnse/request-otp', methods=['POST'])
def dnse_request_otp():
    """Request OTP for trading token using UI client"""
    if not UI_DNSE_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'DNSE UI client not available',
            'error_type': 'SYSTEM_ERROR',
            'user_message': 'Trading service is not available'
        }), 400
    
    try:
        result = ui_client.request_otp()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'UNEXPECTED_ERROR',
            'user_message': 'An unexpected error occurred while requesting OTP'
        }), 500

@app.route('/api/dnse/verify-otp', methods=['POST'])
def dnse_verify_otp():
    """Verify OTP and get trading token using UI client"""
    if not UI_DNSE_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'DNSE UI client not available',
            'error_type': 'SYSTEM_ERROR',
            'user_message': 'Trading service is not available'
        }), 400
    
    try:
        data = request.get_json()
        otp_code = data.get('otp_code')
        
        result = ui_client.verify_otp(otp_code)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'UNEXPECTED_ERROR',
            'user_message': 'An unexpected error occurred during OTP verification'
        }), 500

@app.route('/api/dnse/accounts', methods=['GET'])
def dnse_get_accounts():
    """Get trading accounts using UI client"""
    if not UI_DNSE_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'DNSE UI client not available',
            'error_type': 'SYSTEM_ERROR',
            'user_message': 'Trading service is not available'
        }), 400
    
    try:
        result = ui_client.get_accounts()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'UNEXPECTED_ERROR',
            'user_message': 'An unexpected error occurred while loading accounts'
        }), 500

@app.route('/api/dnse/portfolio/<account_no>', methods=['GET'])
def dnse_get_portfolio(account_no):
    """Get portfolio for specific account"""
    global dnse_client
    
    if not dnse_client or not dnse_client.is_authenticated():
        return jsonify({
            'success': False,
            'error': 'Must login first'
        }), 401
    
    try:
        portfolio = dnse_client.get_portfolio(account_no)
        
        return jsonify({
            'success': True,
            'portfolio': portfolio
        })
        
    except DNSEAPIError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/dnse/buying-power/<account_no>', methods=['GET'])
def dnse_get_buying_power(account_no):
    """Get buying power for specific account"""
    global dnse_client
    
    if not dnse_client or not dnse_client.is_authenticated():
        return jsonify({
            'success': False,
            'error': 'Must login first'
        }), 401
    
    try:
        buying_power = dnse_client.get_buying_power(account_no)
        
        return jsonify({
            'success': True,
            'buying_power': buying_power
        })
        
    except DNSEAPIError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/dnse/pending-orders/<account_no>', methods=['GET'])
def dnse_get_pending_orders(account_no):
    """Get pending orders for specific account"""
    global dnse_client
    
    if not dnse_client or not dnse_client.is_authenticated():
        return jsonify({
            'success': False,
            'error': 'Must login first'
        }), 401
    
    try:
        orders = dnse_client.get_pending_orders(account_no)
        
        return jsonify({
            'success': True,
            'orders': orders
        })
        
    except DNSEAPIError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/dnse/market-data/<symbol>', methods=['GET'])
def dnse_get_market_data(symbol):
    """Get market data for a symbol using DNSE"""
    global dnse_client
    
    if not dnse_client or not dnse_client.is_authenticated():
        return jsonify({
            'success': False,
            'error': 'Must login first'
        }), 401
    
    try:
        market_data = dnse_client.get_market_data(symbol)
        
        return jsonify({
            'success': True,
            'market_data': {
                'symbol': market_data.symbol,
                'price': market_data.price,
                'high': market_data.high,
                'low': market_data.low,
                'volume': market_data.volume,
                'timestamp': market_data.timestamp.isoformat() if market_data.timestamp else None
            }
        })
        
    except DNSEAPIError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/dnse/place-order', methods=['POST'])
def dnse_place_order():
    """Place order through DNSE"""
    global dnse_client
    
    if not dnse_client or not dnse_client.is_authenticated() or not dnse_client.has_trading_token():
        return jsonify({
            'success': False,
            'error': 'Must login and verify OTP first'
        }), 401
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['symbol', 'side', 'quantity', 'price', 'account_no']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Convert side to OrderSide enum
        side_map = {
            'buy': OrderSide.BUY,
            'sell': OrderSide.SELL
        }
        
        order_side = side_map.get(data['side'].lower())
        if not order_side:
            return jsonify({
                'success': False,
                'error': 'Invalid order side. Must be "buy" or "sell"'
            }), 400
        
        # Convert order type
        order_type_map = {
            'limit': OrderType.LIMIT,
            'market': OrderType.MARKET
        }
        
        order_type = order_type_map.get(data.get('order_type', 'limit').lower(), OrderType.LIMIT)
        
        # Create order request
        order_request = OrderRequest(
            symbol=data['symbol'],
            side=order_side,
            quantity=data['quantity'],
            price=data['price'],
            order_type=order_type,
            account_no=data['account_no']
        )
        
        # Place order
        result = dnse_client.place_order(order_request)
        
        return jsonify({
            'success': True,
            'order_result': result
        })
        
    except DNSEAPIError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/dnse/cancel-order', methods=['POST'])
def dnse_cancel_order():
    """Cancel order through DNSE"""
    global dnse_client
    
    if not dnse_client or not dnse_client.is_authenticated() or not dnse_client.has_trading_token():
        return jsonify({
            'success': False,
            'error': 'Must login and verify OTP first'
        }), 401
    
    try:
        data = request.get_json()
        
        if not data.get('order_id') or not data.get('account_no'):
            return jsonify({
                'success': False,
                'error': 'order_id and account_no are required'
            }), 400
        
        result = dnse_client.cancel_order(data['order_id'], data['account_no'])
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except DNSEAPIError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/dnse/status', methods=['GET'])
def dnse_status():
    """Get DNSE client status using UI client"""
    if not UI_DNSE_AVAILABLE:
        return jsonify({
            'dnse_available': False,
            'ui_client_available': False,
            'error': 'DNSE UI client not available'
        })
    
    try:
        status = ui_client.get_session_status()
        return jsonify(status)
        
    except Exception as e:
        return jsonify({
            'dnse_available': DNSE_AVAILABLE,
            'ui_client_available': UI_DNSE_AVAILABLE,
            'error': str(e)
        })

# =============================================================================
# Enhanced UI DNSE Endpoints
# =============================================================================

@app.route('/api/dnse/account/select', methods=['POST'])
def dnse_select_account():
    """Select an account for trading using UI client"""
    if not UI_DNSE_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'DNSE UI client not available',
            'error_type': 'SYSTEM_ERROR',
            'user_message': 'Trading service is not available'
        }), 400
    
    try:
        data = request.get_json()
        account_index = data.get('account_index')
        
        if account_index is None:
            return jsonify({
                'success': False,
                'error': 'Missing account_index',
                'error_type': 'VALIDATION_ERROR',
                'user_message': 'Please provide account index'
            }), 400
        
        result = ui_client.select_account(account_index)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'UNEXPECTED_ERROR',
            'user_message': 'An unexpected error occurred while selecting account'
        }), 500

@app.route('/api/dnse/portfolio', methods=['GET'])
def dnse_get_portfolio_ui():
    """Get portfolio for selected account using UI client"""
    if not UI_DNSE_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'DNSE UI client not available',
            'error_type': 'SYSTEM_ERROR',
            'user_message': 'Trading service is not available'
        }), 400
    
    try:
        account_index = request.args.get('account_index', type=int)
        result = ui_client.get_portfolio(account_index)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'UNEXPECTED_ERROR',
            'user_message': 'An unexpected error occurred while loading portfolio'
        }), 500

@app.route('/api/dnse/market-data/<symbol>', methods=['GET'])  
def dnse_get_market_data_ui(symbol):
    """Get market data using UI client with caching"""
    if not UI_DNSE_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'DNSE UI client not available',
            'error_type': 'SYSTEM_ERROR',
            'user_message': 'Trading service is not available'
        }), 400
    
    try:
        force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
        result = ui_client.get_market_data(symbol.upper(), force_refresh)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'UNEXPECTED_ERROR',
            'user_message': f'An unexpected error occurred while loading market data for {symbol}'
        }), 500

@app.route('/api/dnse/orders/place', methods=['POST'])
def dnse_place_order_ui():
    """Place order using UI client with enhanced validation"""
    if not UI_DNSE_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'DNSE UI client not available',
            'error_type': 'SYSTEM_ERROR',
            'user_message': 'Trading service is not available'
        }), 400
    
    try:
        order_data = request.get_json()
        result = ui_client.place_order(order_data)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'UNEXPECTED_ERROR',
            'user_message': 'An unexpected error occurred while placing order'
        }), 500

@app.route('/api/dnse/orders/pending', methods=['GET'])
def dnse_get_pending_orders_ui():
    """Get pending orders using UI client"""
    if not UI_DNSE_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'DNSE UI client not available',
            'error_type': 'SYSTEM_ERROR',
            'user_message': 'Trading service is not available'
        }), 400
    
    try:
        account_index = request.args.get('account_index', type=int)
        result = ui_client.get_pending_orders(account_index)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'UNEXPECTED_ERROR',
            'user_message': 'An unexpected error occurred while loading orders'
        }), 500

@app.route('/api/dnse/orders/cancel', methods=['POST'])
def dnse_cancel_order_ui():
    """Cancel order using UI client"""
    if not UI_DNSE_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'DNSE UI client not available',
            'error_type': 'SYSTEM_ERROR',
            'user_message': 'Trading service is not available'
        }), 400
    
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        account_index = data.get('account_index')
        
        result = ui_client.cancel_order(order_id, account_index)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'UNEXPECTED_ERROR',
            'user_message': 'An unexpected error occurred while cancelling order'
        }), 500

@app.route('/api/dnse/logout', methods=['POST'])
def dnse_logout():
    """Logout from DNSE using UI client"""
    if not UI_DNSE_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'DNSE UI client not available',
            'error_type': 'SYSTEM_ERROR',
            'user_message': 'Trading service is not available'
        }), 400
    
    try:
        global dnse_client, active_client_type
        result = ui_client.logout()
        
        # Clear global references
        dnse_client = None
        active_client_type = None
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'UNEXPECTED_ERROR',
            'user_message': 'An unexpected error occurred during logout'
        }), 500

# =============================================================================
# End DNSE Trading API Endpoints (Including UI Enhanced Endpoints)
# =============================================================================

# =============================================================================
# Demo Trading Client API Endpoints
# =============================================================================

@app.route('/api/demo/login', methods=['POST'])
def demo_login():
    """Login to demo client"""
    global demo_client, active_client_type
    
    if not DEMO_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Demo client not available. Check installation and dependencies.'
        }), 400
    
    try:
        data = request.get_json()
        username = data.get('username', 'demo_user')
        password = data.get('password', 'demo_pass')
        initial_balance = data.get('initial_balance', 100000000)  # 100M VND default
        
        # Initialize demo client
        demo_client = DemoTradingClient(username=username, password=password, initial_balance=initial_balance)
        
        # Authenticate
        success = demo_client.authenticate()
        
        if success:
            active_client_type = 'demo'
            
            return jsonify({
                'success': True,
                'message': 'Demo authentication successful',
                'client_type': 'DEMO',
                'initial_balance': initial_balance,
                'accounts': demo_client.get_accounts()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Demo authentication failed'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/demo/accounts', methods=['GET'])
def demo_get_accounts():
    """Get demo trading accounts"""
    global demo_client
    
    if not demo_client or not demo_client.is_authenticated:
        return jsonify({
            'success': False,
            'error': 'Must login to demo client first'
        }), 401
    
    try:
        accounts = demo_client.get_accounts()
        
        return jsonify({
            'success': True,
            'accounts': accounts
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/demo/portfolio/<account_no>', methods=['GET'])
def demo_get_portfolio(account_no):
    """Get demo portfolio for specific account"""
    global demo_client
    
    if not demo_client or not demo_client.is_authenticated:
        return jsonify({
            'success': False,
            'error': 'Must login to demo client first'
        }), 401
    
    try:
        portfolio = demo_client.get_portfolio(account_no)
        
        return jsonify({
            'success': True,
            'portfolio': portfolio
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/demo/buying-power/<account_no>', methods=['GET'])
def demo_get_buying_power(account_no):
    """Get demo buying power for specific account"""
    global demo_client
    
    if not demo_client or not demo_client.is_authenticated:
        return jsonify({
            'success': False,
            'error': 'Must login to demo client first'
        }), 401
    
    try:
        buying_power = demo_client.get_buying_power(account_no)
        
        return jsonify({
            'success': True,
            'buying_power': buying_power
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/demo/market-data/<symbol>', methods=['GET'])
def demo_get_market_data(symbol):
    """Get demo market data for a symbol"""
    global demo_client
    
    if not demo_client or not demo_client.is_authenticated:
        return jsonify({
            'success': False,
            'error': 'Must login to demo client first'
        }), 401
    
    try:
        market_data = demo_client.get_market_data(symbol)
        
        return jsonify({
            'success': True,
            'market_data': {
                'symbol': market_data.symbol,
                'price': market_data.price,
                'change': market_data.change,
                'change_percent': market_data.change_percent,
                'volume': market_data.volume,
                'high': market_data.high,
                'low': market_data.low,
                'open': market_data.open,
                'close': market_data.close,
                'bid': market_data.bid,
                'ask': market_data.ask,
                'timestamp': market_data.timestamp.isoformat() if market_data.timestamp else None
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/demo/place-order', methods=['POST'])
def demo_place_order():
    """Place order through demo client"""
    global demo_client
    
    if not demo_client or not demo_client.is_authenticated:
        return jsonify({
            'success': False,
            'error': 'Must login to demo client first'
        }), 401
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['symbol', 'side', 'quantity', 'price', 'account_no']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Convert side to OrderSide enum
        side_map = {
            'buy': OrderSide.BUY,
            'sell': OrderSide.SELL
        }
        
        order_side = side_map.get(data['side'].lower())
        if not order_side:
            return jsonify({
                'success': False,
                'error': 'Invalid order side. Must be "buy" or "sell"'
            }), 400
        
        # Convert order type
        order_type_map = {
            'limit': OrderType.LIMIT,
            'market': OrderType.MARKET
        }
        
        order_type = order_type_map.get(data.get('order_type', 'limit').lower(), OrderType.LIMIT)
        
        # Create order request
        order_request = OrderRequest(
            symbol=data['symbol'],
            side=order_side,
            quantity=data['quantity'],
            price=data['price'],
            order_type=order_type,
            account_no=data['account_no']
        )
        
        # Place order
        result = demo_client.place_order(order_request)
        
        return jsonify({
            'success': True,
            'order_result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/demo/cancel-order', methods=['POST'])
def demo_cancel_order():
    """Cancel order through demo client"""
    global demo_client
    
    if not demo_client or not demo_client.is_authenticated:
        return jsonify({
            'success': False,
            'error': 'Must login to demo client first'
        }), 401
    
    try:
        data = request.get_json()
        
        order_id = data.get('order_id')
        account_no = data.get('account_no')
        
        if not order_id or not account_no:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: order_id and account_no'
            }), 400
        
        # Cancel order
        result = demo_client.cancel_order(order_id, account_no)
        
        return jsonify({
            'success': True,
            'cancel_result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/demo/pending-orders/<account_no>', methods=['GET'])
def demo_get_pending_orders(account_no):
    """Get pending orders for demo account"""
    global demo_client
    
    if not demo_client or not demo_client.is_authenticated:
        return jsonify({
            'success': False,
            'error': 'Must login to demo client first'
        }), 401
    
    try:
        orders = demo_client.get_pending_orders(account_no)
        
        return jsonify({
            'success': True,
            'orders': orders
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/demo/order-history/<account_no>', methods=['GET'])
def demo_get_order_history(account_no):
    """Get order history for demo account"""
    global demo_client
    
    if not demo_client or not demo_client.is_authenticated:
        return jsonify({
            'success': False,
            'error': 'Must login to demo client first'
        }), 401
    
    try:
        limit = request.args.get('limit', 50, type=int)
        orders = demo_client.get_order_history(account_no, limit)
        
        # Convert datetime objects to strings for JSON serialization
        serialized_orders = []
        for order in orders:
            order_copy = order.copy()
            if 'timestamp' in order_copy and order_copy['timestamp']:
                order_copy['timestamp'] = order_copy['timestamp'].isoformat()
            if 'cancelled_time' in order_copy and order_copy['cancelled_time']:
                order_copy['cancelled_time'] = order_copy['cancelled_time'].isoformat()
            serialized_orders.append(order_copy)
        
        return jsonify({
            'success': True,
            'orders': serialized_orders
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/demo/market-conditions', methods=['POST'])
def demo_set_market_conditions():
    """Set demo market conditions"""
    global demo_client
    
    if not demo_client or not demo_client.is_authenticated:
        return jsonify({
            'success': False,
            'error': 'Must login to demo client first'
        }), 401
    
    try:
        data = request.get_json()
        
        trend = data.get('trend', 'NEUTRAL')
        volatility_multiplier = data.get('volatility_multiplier', 1.0)
        
        # Validate trend
        valid_trends = ['BULLISH', 'BEARISH', 'NEUTRAL']
        if trend not in valid_trends:
            return jsonify({
                'success': False,
                'error': f'Invalid trend. Must be one of: {valid_trends}'
            }), 400
        
        # Set market conditions
        demo_client.set_market_conditions(trend, volatility_multiplier)
        
        return jsonify({
            'success': True,
            'message': f'Market conditions set to {trend} with {volatility_multiplier}x volatility'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/demo/simulate-movement', methods=['POST'])
def demo_simulate_movement():
    """Simulate market movement for a symbol"""
    global demo_client
    
    if not demo_client or not demo_client.is_authenticated:
        return jsonify({
            'success': False,
            'error': 'Must login to demo client first'
        }), 401
    
    try:
        data = request.get_json()
        
        symbol = data.get('symbol')
        price_change_percent = data.get('price_change_percent')
        
        if not symbol or price_change_percent is None:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: symbol and price_change_percent'
            }), 400
        
        # Simulate movement
        demo_client.simulate_market_movement(symbol, price_change_percent)
        
        return jsonify({
            'success': True,
            'message': f'Simulated {price_change_percent:.2f}% movement for {symbol}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/demo/reset-portfolio', methods=['POST'])
def demo_reset_portfolio():
    """Reset demo portfolio to initial state"""
    global demo_client
    
    if not demo_client or not demo_client.is_authenticated:
        return jsonify({
            'success': False,
            'error': 'Must login to demo client first'
        }), 401
    
    try:
        data = request.get_json()
        account_no = data.get('account_no')
        
        if not account_no:
            return jsonify({
                'success': False,
                'error': 'Missing required field: account_no'
            }), 400
        
        # Reset portfolio
        demo_client.reset_portfolio(account_no)
        
        return jsonify({
            'success': True,
            'message': f'Portfolio reset for account {account_no}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/demo/status', methods=['GET'])
def demo_status():
    """Get demo client status"""
    global demo_client
    
    status = {
        'demo_available': DEMO_AVAILABLE,
        'client_initialized': demo_client is not None,
        'authenticated': demo_client.is_authenticated if demo_client else False,
    }
    
    if demo_client:
        status.update(demo_client.get_status())
    
    return jsonify(status)

# =============================================================================
# Trading Client Management Endpoints
# =============================================================================

@app.route('/api/trading/active-client', methods=['GET'])
def get_active_client():
    """Get information about the currently active trading client"""
    global active_client_type, dnse_client, demo_client
    
    return jsonify({
        'active_client_type': active_client_type,
        'dnse_available': DNSE_AVAILABLE,
        'demo_available': DEMO_AVAILABLE,
        'dnse_authenticated': dnse_client.is_authenticated() if dnse_client else False,
        'demo_authenticated': demo_client.is_authenticated if demo_client else False
    })

@app.route('/api/trading/switch-client', methods=['POST'])
def switch_client():
    """Switch between DNSE and demo trading clients"""
    global active_client_type
    
    try:
        data = request.get_json()
        client_type = data.get('client_type')
        
        if client_type not in ['dnse', 'demo']:
            return jsonify({
                'success': False,
                'error': 'Invalid client type. Must be "dnse" or "demo"'
            }), 400
        
        # Check if requested client is available and authenticated
        if client_type == 'dnse':
            if not DNSE_AVAILABLE:
                return jsonify({
                    'success': False,
                    'error': 'DNSE client not available'
                }), 400
            if not dnse_client or not dnse_client.is_authenticated():
                return jsonify({
                    'success': False,
                    'error': 'DNSE client not authenticated'
                }), 401
        elif client_type == 'demo':
            if not DEMO_AVAILABLE:
                return jsonify({
                    'success': False,
                    'error': 'Demo client not available'
                }), 400
            if not demo_client or not demo_client.is_authenticated:
                return jsonify({
                    'success': False,
                    'error': 'Demo client not authenticated'
                }), 401
        
        active_client_type = client_type
        
        return jsonify({
            'success': True,
            'active_client_type': active_client_type,
            'message': f'Switched to {client_type.upper()} client'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

# =============================================================================
# End Demo Trading Client API Endpoints  
# =============================================================================

@app.route('/api/test-strategy', methods=['POST'])
def test_strategy():
    """Test a strategy with mock data"""
    try:
        data = request.get_json()
        strategy_code = data.get('strategy_code', '')
        parameters = data.get('parameters', {})
        
        # Generate small dataset for quick test
        mock_data = generate_mock_price_data(days=10)
        
        # Test strategy execution
        trades, equity_curve = execute_strategy(strategy_code, mock_data, parameters)
        
        return jsonify({
            'success': True,
            'message': 'Strategy test completed successfully',
            'result': {
                'trades': len(trades),
                'final_value': equity_curve[-1] if equity_curve else 0,
                'sample_trades': trades[:5]  # Return first 5 trades
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/backtest', methods=['POST'])
def backtest_strategy():
    """Run full backtest on a strategy"""
    try:
        data = request.get_json()
        strategy_code = data.get('strategy_code', '')
        parameters = data.get('parameters', {})
        symbol = data.get('symbol', 'VN30F2412')
        start_date = data.get('start_date', '2024-01-01')
        end_date = data.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        
        # Get real market data (fallback to mock if fails)
        try:
            price_data = get_real_market_data(symbol, start_date, end_date)
            data_source = 'vnstock_real_data'
        except Exception as e:
            print(f"Failed to get real data, using mock: {str(e)}")
            days = (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days
            price_data = generate_mock_price_data(symbol, max(days, 100))
            data_source = 'mock_data'
        
        # Execute backtest
        trades, equity_curve = execute_strategy(strategy_code, price_data, parameters)
        
        # Calculate metrics
        metrics = calculate_metrics(equity_curve, trades)
        
        # Prepare response
        result = {
            'metrics': metrics,
            'equity_curve': {
                'dates': [bar['date'] for bar in price_data],
                'values': equity_curve
            },
            'drawdown': {
                'dates': [bar['date'] for bar in price_data],
                'values': [(equity_curve[i] - max(equity_curve[:i+1])) / max(equity_curve[:i+1]) 
                          for i in range(len(equity_curve))]
            },
            'trades': trades,
            'price_data': {
                'dates': [bar['date'] for bar in price_data],
                'prices': [bar['close'] for bar in price_data]
            },
            'data_source': data_source
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/market/quote/<symbol>', methods=['GET'])
def get_quote(symbol):
    """Get current market quote for a symbol"""
    try:
        quote = get_current_quote(symbol.upper())
        return jsonify({
            'success': True,
            'data': quote
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/market/history/<symbol>', methods=['GET'])
def get_history(symbol):
    """Get historical market data for a symbol"""
    try:
        start_date = request.args.get('start', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
        interval = request.args.get('interval', '1D')
        
        data = get_real_market_data(symbol.upper(), start_date, end_date, interval)
        
        return jsonify({
            'success': True,
            'data': data,
            'symbol': symbol.upper(),
            'start_date': start_date,
            'end_date': end_date,
            'interval': interval
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/market/overview', methods=['GET'])
def market_overview():
    """Get market overview with multiple symbols"""
    try:
        overview = get_market_overview()
        return jsonify({
            'success': True,
            'data': overview,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/backtest/real', methods=['POST'])
def backtest_strategy_real():
    """Run backtest with real market data"""
    try:
        data = request.get_json()
        strategy_code = data.get('strategy_code', '')
        parameters = data.get('parameters', {})
        symbol = data.get('symbol', 'VCI')
        start_date = data.get('start_date', (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'))
        end_date = data.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        
        # Get real market data
        price_data = get_real_market_data(symbol, start_date, end_date)
        
        # Execute backtest
        trades, equity_curve = execute_strategy(strategy_code, price_data, parameters)
        
        # Calculate metrics
        metrics = calculate_metrics(equity_curve, trades)
        
        # Prepare response
        result = {
            'metrics': metrics,
            'equity_curve': {
                'dates': [bar['date'] for bar in price_data],
                'values': equity_curve
            },
            'drawdown': {
                'dates': [bar['date'] for bar in price_data],
                'values': [(equity_curve[i] - max(equity_curve[:i+1])) / max(equity_curve[:i+1])
                          for i in range(len(equity_curve))]
            },
            'trades': trades,
            'price_data': {
                'dates': [bar['date'] for bar in price_data],
                'prices': [bar['close'] for bar in price_data]
            },
            'symbol': symbol,
            'data_source': 'vnstock_real_data'
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("🚀 Starting DNSE Strategy Editor Backend Server...")
    print("📊 Mock data generator initialized")
    print("🔧 Strategy execution engine ready")
    print("💰 Backtesting engine ready")
    print("🌐 Server running on http://localhost:8011")
    
    app.run(host='0.0.0.0', port=8011, debug=True)
