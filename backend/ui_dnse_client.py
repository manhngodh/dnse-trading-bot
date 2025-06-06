"""
UI-Compatible DNSE Trading Client
================================

A DNSE client specifically designed for web UI integration.
This client provides UI-friendly methods, data formatting, and error handling
optimized for the strategy editor web application.

Features:
    - Session management with state persistence
    - UI-friendly data formatting
    - Real-time market data for charts
    - Portfolio analytics for dashboard
    - Order management with UI feedback
    - Error handling with user-friendly messages
"""

import os
import sys
import json
import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from dataclasses import asdict
import requests
from requests.exceptions import HTTPError, RequestException
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

try:
    from src.clients.dnse_client import DNSEClient
    from src.core.data_structures import OrderRequest, OrderSide, OrderType, MarketData
    from src.core.exceptions import DNSEAPIError, TradingBotError
    DNSE_CORE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: DNSE core not available: {e}")
    DNSE_CORE_AVAILABLE = False
    # Create minimal classes for UI compatibility
    class DNSEClient:
        pass
    class OrderRequest:
        pass
    class OrderSide:
        BUY = "BUY"
        SELL = "SELL"
    class OrderType:
        LIMIT = "LIMIT"
        MARKET = "MARKET"
    class MarketData:
        pass
    class DNSEAPIError(Exception):
        pass


class UIDNSEClient:
    """
    UI-Compatible DNSE Trading Client
    
    A wrapper around the core DNSE client that provides UI-specific functionality
    including session management, data formatting, and enhanced error handling.
    """
    
    def __init__(self):
        """Initialize the UI DNSE client"""
        self.core_client: Optional[DNSEClient] = None
        self.session_data: Dict[str, Any] = {
            'authenticated': False,
            'has_trading_token': False,
            'investor_info': None,
            'accounts': [],
            'selected_account': None,
            'loan_packages': [],
            'last_activity': None,
            'session_start': None
        }
        self.market_cache: Dict[str, Dict] = {}
        self.cache_expiry = 30  # seconds
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def get_session_status(self) -> Dict[str, Any]:
        """
        Get current session status for UI
        
        Returns:
            Dictionary with session information
        """
        return {
            'core_available': DNSE_CORE_AVAILABLE,
            'client_initialized': self.core_client is not None,
            'authenticated': self.session_data['authenticated'],
            'has_trading_token': self.session_data['has_trading_token'],
            'investor_info': self.session_data['investor_info'],
            'accounts_count': len(self.session_data['accounts']),
            'selected_account': self.session_data['selected_account'],
            'last_activity': self.session_data['last_activity'],
            'session_duration': self._get_session_duration(),
            'is_session_valid': self._is_session_valid()
        }
    
    def login(self, username: Optional[str] = None, password: Optional[str] = None) -> Dict[str, Any]:
        """
        Login to DNSE with UI-friendly response
        
        Args:
            username: DNSE username (optional, will load from env if not provided)
            password: DNSE password (optional, will load from env if not provided)
            
        Returns:
            UI-friendly login response
        """
        if not DNSE_CORE_AVAILABLE:
            return {
                'success': False,
                'error': 'DNSE core client is not available',
                'error_type': 'SYSTEM_ERROR',
                'user_message': 'System error: Trading service unavailable'
            }
        
        try:
            # Initialize core client
            self.core_client = DNSEClient(username=username, password=password)
            
            # Authenticate
            success = self.core_client.authenticate()
            
            if success:
                # Get investor info
                investor_info = self.core_client.get_investor_info()
                
                # Update session
                self.session_data.update({
                    'authenticated': True,
                    'investor_info': investor_info,
                    'session_start': datetime.now().isoformat(),
                    'last_activity': datetime.now().isoformat()
                })
                
                return {
                    'success': True,
                    'message': 'Login successful',
                    'investor_info': investor_info,
                    'session_status': self.get_session_status()
                }
            else:
                return {
                    'success': False,
                    'error': 'Authentication failed',
                    'error_type': 'AUTH_ERROR',
                    'user_message': 'Invalid username or password'
                }
                
        except DNSEAPIError as e:
            error_msg = str(e)
            user_msg = 'Login failed. Please check your credentials.'
            
            if 'HTTP 401' in error_msg:
                user_msg = 'Invalid username or password'
            elif 'HTTP 503' in error_msg:
                user_msg = 'Trading service temporarily unavailable'
            elif 'timeout' in error_msg.lower():
                user_msg = 'Connection timeout. Please try again.'
            
            return {
                'success': False,
                'error': error_msg,
                'error_type': 'API_ERROR',
                'user_message': user_msg
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'UNEXPECTED_ERROR',
                'user_message': 'An unexpected error occurred. Please try again.'
            }
    
    def request_otp(self) -> Dict[str, Any]:
        """
        Request OTP for trading with UI-friendly response
        
        Returns:
            UI-friendly OTP request response
        """
        if not self._check_authentication():
            return self._auth_required_response()
        
        try:
            success = self.core_client.request_otp_email()
            
            self._update_activity()
            
            return {
                'success': success,
                'message': 'OTP sent to your registered email' if success else 'Failed to send OTP',
                'user_message': 'Please check your email for the OTP code'
            }
            
        except DNSEAPIError as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'API_ERROR',
                'user_message': 'Failed to send OTP. Please try again later.'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'UNEXPECTED_ERROR',
                'user_message': 'An unexpected error occurred while requesting OTP'
            }
    
    def verify_otp(self, otp_code: str) -> Dict[str, Any]:
        """
        Verify OTP and enable trading
        
        Args:
            otp_code: The OTP code from email
            
        Returns:
            UI-friendly OTP verification response
        """
        if not self._check_authentication():
            return self._auth_required_response()
        
        if not otp_code or len(otp_code.strip()) != 6:
            return {
                'success': False,
                'error': 'Invalid OTP format',
                'error_type': 'VALIDATION_ERROR',
                'user_message': 'Please enter a valid 6-digit OTP code'
            }
        
        try:
            trading_token = self.core_client.verify_otp_email(otp_code.strip())
            
            # Update session
            self.session_data['has_trading_token'] = True
            self._update_activity()
            
            return {
                'success': True,
                'message': 'OTP verified successfully',
                'user_message': 'Trading enabled successfully',
                'session_status': self.get_session_status()
            }
            
        except DNSEAPIError as e:
            error_msg = str(e)
            user_msg = 'Invalid OTP code. Please try again.'
            
            if 'expired' in error_msg.lower():
                user_msg = 'OTP code has expired. Please request a new one.'
            elif 'invalid' in error_msg.lower():
                user_msg = 'Invalid OTP code. Please check and try again.'
            
            return {
                'success': False,
                'error': error_msg,
                'error_type': 'OTP_ERROR',
                'user_message': user_msg
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'UNEXPECTED_ERROR',
                'user_message': 'An unexpected error occurred during OTP verification'
            }
    
    def get_accounts(self) -> Dict[str, Any]:
        """
        Get trading accounts with UI formatting
        
        Returns:
            UI-friendly accounts response
        """
        if not self._check_authentication():
            return self._auth_required_response()
        
        try:
            accounts = self.core_client.get_accounts()
            
            # Format accounts for UI
            formatted_accounts = []
            for i, account in enumerate(accounts):
                formatted_account = {
                    'index': i,
                    'id': account.get('id'),
                    'accountNo': account.get('accountNo') or account.get('account_no'),
                    'accountName': account.get('accountName') or account.get('name', f'Account {i+1}'),
                    'status': account.get('status', 'ACTIVE'),
                    'type': account.get('type', 'NORMAL'),
                    'currency': account.get('currency', 'VND'),
                    'isDefault': i == 0  # Mark first account as default
                }
                formatted_accounts.append(formatted_account)
            
            # Update session
            self.session_data['accounts'] = formatted_accounts
            if formatted_accounts and not self.session_data['selected_account']:
                self.session_data['selected_account'] = formatted_accounts[0]
            
            self._update_activity()
            
            return {
                'success': True,
                'accounts': formatted_accounts,
                'selected_account': self.session_data['selected_account'],
                'total_accounts': len(formatted_accounts)
            }
            
        except DNSEAPIError as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'API_ERROR',
                'user_message': 'Failed to load trading accounts'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'UNEXPECTED_ERROR',
                'user_message': 'An unexpected error occurred while loading accounts'
            }
    
    def select_account(self, account_index: int) -> Dict[str, Any]:
        """
        Select an account for trading
        
        Args:
            account_index: Index of account to select
            
        Returns:
            UI-friendly account selection response
        """
        if not self.session_data['accounts']:
            return {
                'success': False,
                'error': 'No accounts available',
                'error_type': 'NO_ACCOUNTS',
                'user_message': 'Please load accounts first'
            }
        
        if account_index < 0 or account_index >= len(self.session_data['accounts']):
            return {
                'success': False,
                'error': 'Invalid account index',
                'error_type': 'VALIDATION_ERROR',
                'user_message': 'Invalid account selection'
            }
        
        selected_account = self.session_data['accounts'][account_index]
        self.session_data['selected_account'] = selected_account
        self._update_activity()
        
        return {
            'success': True,
            'selected_account': selected_account,
            'message': f'Account {selected_account["accountName"]} selected'
        }
    
    def get_portfolio(self, account_index: Optional[int] = None) -> Dict[str, Any]:
        """
        Get portfolio information with UI formatting
        
        Args:
            account_index: Account index (uses selected account if None)
            
        Returns:
            UI-friendly portfolio response
        """
        if not self._check_authentication():
            return self._auth_required_response()
        
        account = self._get_account(account_index)
        if not account:
            return self._no_account_response()
        
        try:
            portfolio = self.core_client.get_portfolio(account['accountNo'])
            
            # Format portfolio for UI
            formatted_portfolio = {
                'accountNo': account['accountNo'],
                'accountName': account['accountName'],
                'summary': {
                    'totalMarketValue': portfolio.get('totalMarketValue', 0),
                    'totalCostValue': portfolio.get('totalCostValue', 0),
                    'totalPnL': portfolio.get('totalPnL', 0),
                    'pnlPercent': portfolio.get('pnlPercent', 0),
                    'cashBalance': portfolio.get('cashBalance', 0),
                    'buyingPower': portfolio.get('buyingPower', 0),
                    'currency': portfolio.get('currency', 'VND')
                },
                'holdings': [],
                'performance': {
                    'dayChange': 0,
                    'dayChangePercent': 0,
                    'totalReturn': portfolio.get('pnlPercent', 0),
                    'totalReturnAmount': portfolio.get('totalPnL', 0)
                },
                'asOfDate': portfolio.get('asOfDate', datetime.now().isoformat()),
                'lastUpdated': datetime.now().isoformat()
            }
            
            # Format holdings
            for holding in portfolio.get('securities', []):
                formatted_holding = {
                    'symbol': holding.get('symbol'),
                    'quantity': holding.get('quantity', 0),
                    'marketPrice': holding.get('marketPrice', 0),
                    'costPrice': holding.get('costPrice', 0),
                    'marketValue': holding.get('marketValue', 0),
                    'costValue': holding.get('costValue', 0),
                    'pnl': holding.get('pnl', 0),
                    'pnlPercent': holding.get('pnlPercent', 0),
                    'dayChange': holding.get('dayChange', 0),
                    'dayChangePercent': holding.get('dayChangePercent', 0),
                    'sellableQuantity': holding.get('sellableQuantity', 0),
                    'weight': 0  # Calculate weight
                }
                
                # Calculate weight
                if formatted_portfolio['summary']['totalMarketValue'] > 0:
                    formatted_holding['weight'] = (formatted_holding['marketValue'] / 
                                                 formatted_portfolio['summary']['totalMarketValue']) * 100
                
                formatted_portfolio['holdings'].append(formatted_holding)
            
            self._update_activity()
            
            return {
                'success': True,
                'portfolio': formatted_portfolio
            }
            
        except DNSEAPIError as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'API_ERROR',
                'user_message': 'Failed to load portfolio data'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'UNEXPECTED_ERROR',
                'user_message': 'An unexpected error occurred while loading portfolio'
            }
    
    def get_market_data(self, symbol: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get market data with caching for UI performance
        
        Args:
            symbol: Stock symbol
            force_refresh: Force refresh cache
            
        Returns:
            UI-friendly market data response
        """
        if not self._check_authentication():
            return self._auth_required_response()
        
        # Check cache
        if not force_refresh and symbol in self.market_cache:
            cache_entry = self.market_cache[symbol]
            cache_time = datetime.fromisoformat(cache_entry['timestamp'])
            if datetime.now() - cache_time < timedelta(seconds=self.cache_expiry):
                return {
                    'success': True,
                    'market_data': cache_entry['data'],
                    'cached': True
                }
        
        try:
            market_data = self.core_client.get_market_data(symbol)
            
            # Format for UI
            formatted_data = {
                'symbol': market_data.symbol,
                'price': market_data.price,
                'change': market_data.change,
                'changePercent': market_data.change_percent,
                'volume': market_data.volume,
                'high': market_data.high,
                'low': market_data.low,
                'open': market_data.open,
                'close': market_data.close,
                'bid': market_data.bid,
                'ask': market_data.ask,
                'timestamp': market_data.timestamp.isoformat() if market_data.timestamp else datetime.now().isoformat(),
                'status': 'TRADING',  # Assume trading hours
                'exchange': 'HOSE',  # Default exchange
                'lastUpdated': datetime.now().isoformat()
            }
            
            # Cache the data
            self.market_cache[symbol] = {
                'data': formatted_data,
                'timestamp': datetime.now().isoformat()
            }
            
            self._update_activity()
            
            return {
                'success': True,
                'market_data': formatted_data,
                'cached': False
            }
            
        except DNSEAPIError as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'API_ERROR',
                'user_message': f'Failed to load market data for {symbol}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'UNEXPECTED_ERROR',
                'user_message': f'An unexpected error occurred while loading market data for {symbol}'
            }
    
    def place_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Place order with UI-friendly validation and response
        
        Args:
            order_data: Order information from UI
            
        Returns:
            UI-friendly order placement response
        """
        if not self._check_authentication():
            return self._auth_required_response()
        
        if not self.session_data['has_trading_token']:
            return {
                'success': False,
                'error': 'Trading token required',
                'error_type': 'TRADING_TOKEN_REQUIRED',
                'user_message': 'Please verify OTP to enable trading'
            }
        
        # Validate order data
        validation_result = self._validate_order_data(order_data)
        if not validation_result['valid']:
            return {
                'success': False,
                'error': validation_result['error'],
                'error_type': 'VALIDATION_ERROR',
                'user_message': validation_result['user_message']
            }
        
        account = self._get_account(order_data.get('account_index'))
        if not account:
            return self._no_account_response()
        
        try:
            # Create order request
            side = OrderSide.BUY if order_data['side'].upper() == 'BUY' else OrderSide.SELL
            order_type = OrderType.LIMIT if order_data.get('order_type', 'LIMIT').upper() == 'LIMIT' else OrderType.MARKET
            
            order_request = OrderRequest(
                symbol=order_data['symbol'].upper(),
                side=side,
                quantity=int(order_data['quantity']),
                price=float(order_data['price']),
                order_type=order_type,
                account_no=account['accountNo']
            )
            
            # Place order
            result = self.core_client.place_order(order_request)
            
            # Format response for UI
            formatted_result = {
                'orderId': result.get('orderId') or result.get('id'),
                'symbol': order_data['symbol'].upper(),
                'side': order_data['side'].upper(),
                'quantity': int(order_data['quantity']),
                'price': float(order_data['price']),
                'orderType': order_data.get('order_type', 'LIMIT').upper(),
                'status': result.get('status', 'PENDING'),
                'accountNo': account['accountNo'],
                'timestamp': datetime.now().isoformat(),
                'message': result.get('message', 'Order placed successfully')
            }
            
            self._update_activity()
            
            return {
                'success': True,
                'order': formatted_result,
                'user_message': f'Order placed successfully for {order_data["symbol"]}'
            }
            
        except DNSEAPIError as e:
            error_msg = str(e)
            user_msg = 'Order placement failed. Please try again.'
            
            if 'insufficient' in error_msg.lower():
                user_msg = 'Insufficient buying power'
            elif 'invalid price' in error_msg.lower():
                user_msg = 'Invalid price. Please check price limits.'
            elif 'market closed' in error_msg.lower():
                user_msg = 'Market is currently closed'
            
            return {
                'success': False,
                'error': error_msg,
                'error_type': 'ORDER_ERROR',
                'user_message': user_msg
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'UNEXPECTED_ERROR',
                'user_message': 'An unexpected error occurred while placing order'
            }
    
    def get_pending_orders(self, account_index: Optional[int] = None) -> Dict[str, Any]:
        """
        Get pending orders with UI formatting
        
        Args:
            account_index: Account index (uses selected account if None)
            
        Returns:
            UI-friendly pending orders response
        """
        if not self._check_authentication():
            return self._auth_required_response()
        
        account = self._get_account(account_index)
        if not account:
            return self._no_account_response()
        
        try:
            orders = self.core_client.get_pending_orders(account['accountNo'])
            
            # Format orders for UI
            formatted_orders = []
            for order in orders:
                formatted_order = {
                    'orderId': order.get('orderId') or order.get('id'),
                    'symbol': order.get('symbol'),
                    'side': order.get('side'),
                    'quantity': order.get('quantity', 0),
                    'price': order.get('price', 0),
                    'orderType': order.get('orderType', 'LIMIT'),
                    'status': order.get('status', 'PENDING'),
                    'filledQuantity': order.get('filledQuantity', 0),
                    'remainingQuantity': order.get('remainingQuantity', order.get('quantity', 0)),
                    'orderTime': order.get('orderTime', ''),
                    'accountNo': account['accountNo'],
                    'canCancel': order.get('status') in ['PENDING', 'PARTIAL_FILLED']
                }
                formatted_orders.append(formatted_order)
            
            self._update_activity()
            
            return {
                'success': True,
                'orders': formatted_orders,
                'total_orders': len(formatted_orders),
                'account': account
            }
            
        except DNSEAPIError as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'API_ERROR',
                'user_message': 'Failed to load pending orders'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'UNEXPECTED_ERROR',
                'user_message': 'An unexpected error occurred while loading orders'
            }
    
    def cancel_order(self, order_id: str, account_index: Optional[int] = None) -> Dict[str, Any]:
        """
        Cancel order with UI-friendly response
        
        Args:
            order_id: Order ID to cancel
            account_index: Account index (uses selected account if None)
            
        Returns:
            UI-friendly cancellation response
        """
        if not self._check_authentication():
            return self._auth_required_response()
        
        if not self.session_data['has_trading_token']:
            return {
                'success': False,
                'error': 'Trading token required',
                'error_type': 'TRADING_TOKEN_REQUIRED',
                'user_message': 'Please verify OTP to enable trading'
            }
        
        account = self._get_account(account_index)
        if not account:
            return self._no_account_response()
        
        try:
            result = self.core_client.cancel_order(order_id, account['accountNo'])
            
            self._update_activity()
            
            return {
                'success': True,
                'result': result,
                'user_message': 'Order cancelled successfully'
            }
            
        except DNSEAPIError as e:
            error_msg = str(e)
            user_msg = 'Order cancellation failed'
            
            if 'not found' in error_msg.lower():
                user_msg = 'Order not found or already processed'
            elif 'cannot cancel' in error_msg.lower():
                user_msg = 'Order cannot be cancelled at this time'
            
            return {
                'success': False,
                'error': error_msg,
                'error_type': 'CANCEL_ERROR',
                'user_message': user_msg
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'UNEXPECTED_ERROR',
                'user_message': 'An unexpected error occurred while cancelling order'
            }
    
    def logout(self) -> Dict[str, Any]:
        """
        Logout and clear session
        
        Returns:
            UI-friendly logout response
        """
        self.core_client = None
        self.session_data = {
            'authenticated': False,
            'has_trading_token': False,
            'investor_info': None,
            'accounts': [],
            'selected_account': None,
            'loan_packages': [],
            'last_activity': None,
            'session_start': None
        }
        self.market_cache.clear()
        
        return {
            'success': True,
            'message': 'Logged out successfully',
            'user_message': 'You have been logged out'
        }
    
    # Private helper methods
    
    def _check_authentication(self) -> bool:
        """Check if client is authenticated"""
        return (self.core_client is not None and 
                self.session_data['authenticated'] and
                self.core_client.is_authenticated())
    
    def _get_account(self, account_index: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get account by index or return selected account"""
        if account_index is not None:
            if 0 <= account_index < len(self.session_data['accounts']):
                return self.session_data['accounts'][account_index]
            return None
        return self.session_data['selected_account']
    
    def _update_activity(self):
        """Update last activity timestamp"""
        self.session_data['last_activity'] = datetime.now().isoformat()
    
    def _get_session_duration(self) -> Optional[str]:
        """Get session duration in human-readable format"""
        if not self.session_data['session_start']:
            return None
        
        start_time = datetime.fromisoformat(self.session_data['session_start'])
        duration = datetime.now() - start_time
        
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def _is_session_valid(self) -> bool:
        """Check if session is still valid"""
        if not self.session_data['last_activity']:
            return False
        
        last_activity = datetime.fromisoformat(self.session_data['last_activity'])
        return datetime.now() - last_activity < timedelta(hours=8)  # 8 hour session timeout
    
    def _auth_required_response(self) -> Dict[str, Any]:
        """Standard authentication required response"""
        return {
            'success': False,
            'error': 'Authentication required',
            'error_type': 'AUTH_REQUIRED',
            'user_message': 'Please login first'
        }
    
    def _no_account_response(self) -> Dict[str, Any]:
        """Standard no account response"""
        return {
            'success': False,
            'error': 'No account selected',
            'error_type': 'NO_ACCOUNT',
            'user_message': 'Please select a trading account'
        }
    
    def _validate_order_data(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate order data for UI"""
        required_fields = ['symbol', 'side', 'quantity', 'price']
        
        for field in required_fields:
            if field not in order_data or order_data[field] is None:
                return {
                    'valid': False,
                    'error': f'Missing required field: {field}',
                    'user_message': f'Please provide {field}'
                }
        
        # Validate symbol
        symbol = str(order_data['symbol']).strip().upper()
        if not symbol or len(symbol) < 3:
            return {
                'valid': False,
                'error': 'Invalid symbol',
                'user_message': 'Please enter a valid stock symbol'
            }
        
        # Validate side
        if order_data['side'].upper() not in ['BUY', 'SELL']:
            return {
                'valid': False,
                'error': 'Invalid order side',
                'user_message': 'Order side must be BUY or SELL'
            }
        
        # Validate quantity
        try:
            quantity = int(order_data['quantity'])
            if quantity <= 0:
                return {
                    'valid': False,
                    'error': 'Invalid quantity',
                    'user_message': 'Quantity must be greater than 0'
                }
            if quantity % 100 != 0:
                return {
                    'valid': False,
                    'error': 'Invalid lot size',
                    'user_message': 'Quantity must be in multiples of 100 shares'
                }
        except (ValueError, TypeError):
            return {
                'valid': False,
                'error': 'Invalid quantity format',
                'user_message': 'Please enter a valid quantity'
            }
        
        # Validate price
        try:
            price = float(order_data['price'])
            if price <= 0:
                return {
                    'valid': False,
                    'error': 'Invalid price',
                    'user_message': 'Price must be greater than 0'
                }
        except (ValueError, TypeError):
            return {
                'valid': False,
                'error': 'Invalid price format',
                'user_message': 'Please enter a valid price'
            }
        
        return {'valid': True}


# Global UI client instance
ui_dnse_client = UIDNSEClient()
