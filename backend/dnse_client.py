"""
DNSE Trading Client
==================

This module provides a client implementation for the DNSE (Vietnam) stock exchange API.
It implements the ITradingClient interface and provides comprehensive trading functionality.

Features:
    - Authentication with JWT and OTP
    - Account management
    - Order placement and management
    - Market data access
    - Buying power analysis
    - Portfolio management
    - Conditional orders support

Usage:
    from backend.dnse_client import DNSEClient
    
    client = DNSEClient(username="user", password="pass")
    client.authenticate()
    
    # Setup trading session
    session = client.setup_trading_session(otp_code="123456")
    
    # Place orders
    order = client.quick_buy("VIC", 95000, 100)
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import requests
from requests.exceptions import HTTPError
from dotenv import load_dotenv

from interfaces.trading_client import ITradingClient
from core.data_structures import MarketData, OrderRequest, OrderSide, OrderType
from exceptions import DNSEAPIError


class DNSEClient(ITradingClient):
    """
    DNSE Trading API Client
    
    A comprehensive client for interacting with DNSE trading APIs including
    authentication, account management, loan packages, and order placement.
    Implements the ITradingClient interface.
    """
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize DNSE client.
        
        Args:
            username: DNSE username (if not provided, will load from .env)
            password: DNSE password (if not provided, will load from .env)
        """
        # Load environment variables if credentials not provided
        if not username or not password:
            load_dotenv()
            username = username or os.getenv("usernameEntrade")
            password = password or os.getenv("password")
        
        if not username or not password:
            raise DNSEAPIError("Username and password must be provided either as parameters or in .env file")
        
        self.username = username
        self.password = password
        self.jwt_token: Optional[str] = None
        self.trading_token: Optional[str] = None
        self.investor_info: Optional[Dict] = None
        self.accounts: Optional[List[Dict]] = None
        self.loan_packages: Optional[List[Dict]] = None
        
        # API base URLs
        self.base_urls = {
            'user_service': 'https://api.dnse.com.vn/user-service',
            'auth_service': 'https://api.dnse.com.vn/auth-service',
            'order_service': 'https://api.dnse.com.vn/order-service',
            'conditional_order_api': 'https://api.dnse.com.vn/conditional-order-api/v1'
        }
    
    def authenticate(self) -> bool:
        """
        Authenticate with DNSE API and get JWT token.
        
        Returns:
            True if authentication successful, False otherwise
            
        Raises:
            DNSEAPIError: If authentication fails
        """
        try:
            url = f"{self.base_urls['auth_service']}/login"
            payload = {
                "username": self.username,
                "password": self.password
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            response_data = response.json()
            self.jwt_token = response_data.get("token")
            
            if not self.jwt_token:
                raise DNSEAPIError("No access token received from authentication")
            
            return True
            
        except HTTPError as e:
            error_msg = f"Authentication failed: HTTP {e.response.status_code}"
            try:
                error_details = e.response.json()
                error_msg += f" - {error_details}"
            except (ValueError, KeyError):
                pass
            raise DNSEAPIError(error_msg)
        except Exception as e:
            raise DNSEAPIError(f"Authentication failed: {str(e)}")
    
    def request_otp_email(self) -> bool:
        """
        Request OTP via email for trading token.
        
        Returns:
            True if OTP request successful
            
        Raises:
            DNSEAPIError: If OTP request fails
        """
        if not self.jwt_token:
            raise DNSEAPIError("Must authenticate first before requesting OTP")
        
        try:
            url = f"{self.base_urls['auth_service']}/api/email-otp"
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers, json={})
            response.raise_for_status()
            
            return True
            
        except HTTPError as e:
            error_msg = f"OTP request failed: HTTP {e.response.status_code}"
            try:
                error_details = e.response.json()
                error_msg += f" - {error_details}"
            except (ValueError, KeyError):
                pass
            raise DNSEAPIError(error_msg)
        except Exception as e:
            raise DNSEAPIError(f"OTP request failed: {str(e)}")
    
    def verify_otp_email(self, otp_code: str) -> str:
        """
        Verify OTP code and get trading token.
        
        Args:
            otp_code: The OTP code from email
            
        Returns:
            Trading token string
            
        Raises:
            DNSEAPIError: If OTP verification fails
        """
        if not self.jwt_token:
            raise DNSEAPIError("Must authenticate first before verifying OTP")
        
        try:
            url = f"{self.base_urls['order_service']}/trading-token"
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json",
                "otp": otp_code
            }
            
            response = requests.post(url, headers=headers, json={})
            response.raise_for_status()
            
            response_data = response.json()
            self.trading_token = response_data.get("tradingToken")
            
            if not self.trading_token:
                raise DNSEAPIError("No trading token received from OTP verification")
            
            return self.trading_token
            
        except HTTPError as e:
            error_msg = f"OTP verification failed: HTTP {e.response.status_code}"
            try:
                error_details = e.response.json()
                error_msg += f" - {error_details}"
            except (ValueError, KeyError):
                pass
            raise DNSEAPIError(error_msg)
        except Exception as e:
            raise DNSEAPIError(f"OTP verification failed: {str(e)}")
    
    def get_investor_info(self) -> Dict[str, Any]:
        """
        Get investor information.
        
        Returns:
            Dictionary containing investor information
        """
        if not self.jwt_token:
            raise DNSEAPIError("Must authenticate first")
        
        try:
            url = f"{self.base_urls['user_service']}/api/me"
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            self.investor_info = response.json()
            return self.investor_info
            
        except HTTPError as e:
            raise DNSEAPIError(f"Failed to get investor info: HTTP {e.response.status_code}")
        except Exception as e:
            raise DNSEAPIError(f"Failed to get investor info: {str(e)}")
    
    def get_accounts(self) -> List[Dict[str, Any]]:
        """
        Get trading accounts (tiểu khoản).
        
        Returns:
            List of account dictionaries
        """
        if not self.jwt_token:
            raise DNSEAPIError("Must authenticate first")
        
        try:
            url = f"{self.base_urls['user_service']}/user/accounts"
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            self.accounts = response.json()
            return self.accounts
            
        except HTTPError as e:
            raise DNSEAPIError(f"Failed to get accounts: HTTP {e.response.status_code}")
        except Exception as e:
            raise DNSEAPIError(f"Failed to get accounts: {str(e)}")
    
    def get_loan_packages(self, account_id: str) -> List[Dict[str, Any]]:
        """
        Get loan packages for an account.
        
        Args:
            account_id: The account ID
            
        Returns:
            List of loan package dictionaries
        """
        if not self.jwt_token:
            raise DNSEAPIError("Must authenticate first")
        
        try:
            url = f"{self.base_urls['order_service']}/loan-packages"
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            params = {"accountId": account_id}
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            self.loan_packages = response.json()
            return self.loan_packages
            
        except HTTPError as e:
            raise DNSEAPIError(f"Failed to get loan packages: HTTP {e.response.status_code}")
        except Exception as e:
            raise DNSEAPIError(f"Failed to get loan packages: {str(e)}")
    
    def get_buying_power(self, account_no: str) -> Dict[str, Any]:
        """
        Get buying power from PPSE endpoint.
        
        Args:
            account_no: The account number
            
        Returns:
            Dictionary containing buying power information
        """
        if not self.jwt_token:
            raise DNSEAPIError("Must authenticate first")
        
        try:
            url = f"{self.base_urls['order_service']}/ppse/{account_no}"
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except HTTPError as e:
            raise DNSEAPIError(f"Failed to get buying power: HTTP {e.response.status_code}")
        except Exception as e:
            raise DNSEAPIError(f"Failed to get buying power: {str(e)}")
    
    def get_buying_power_ext(self, account_no: str, symbol: str, price: float, loan_package_id: str = None) -> Dict[str, Any]:
        """
        Get enhanced buying/selling power for a specific account, symbol, price, and loan package.
        Implements API: /order-service/accounts/<account>/ppse?symbol=<symbol>&price=<price>&loanPackageId=<loanPackageId>
        """
        if not self.jwt_token:
            raise DNSEAPIError("Must authenticate first")
        try:
            url = f"{self.base_urls['order_service']}/accounts/{account_no}/ppse"
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            params = {"symbol": symbol, "price": price}
            if loan_package_id:
                params["loanPackageId"] = loan_package_id
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            raise DNSEAPIError(f"Failed to get enhanced buying power: HTTP {e.response.status_code}")
        except Exception as e:
            raise DNSEAPIError(f"Failed to get enhanced buying power: {str(e)}")
    
    def get_max_buy_quantity(self, symbol: str, price: float, account_no: str) -> int:
        """
        Get maximum buyable quantity for a symbol.
        
        Args:
            symbol: Stock symbol
            price: Price per share
            account_no: Account number
            
        Returns:
            Maximum buyable quantity
        """
        try:
            buying_power_data = self.get_buying_power(account_no)
            buying_power = buying_power_data.get('buyingPower', 0)
            
            if buying_power <= 0 or price <= 0:
                return 0
            
            max_quantity = int(buying_power / price)
            
            # Round down to lot size (100 shares)
            max_quantity = (max_quantity // 100) * 100
            
            return max_quantity
            
        except Exception:
            return 0
    
    def get_max_sell_quantity(self, symbol: str, account_no: str) -> int:
        """
        Get maximum sellable quantity for a symbol.
        
        Args:
            symbol: Stock symbol
            account_no: Account number
            
        Returns:
            Maximum sellable quantity
        """
        try:
            buying_power_data = self.get_buying_power(account_no)
            securities = buying_power_data.get('securities', [])
            
            for security in securities:
                if security.get('symbol') == symbol:
                    return security.get('sellableQuantity', 0)
            
            return 0
            
        except Exception:
            return 0
    
    def check_buying_power(self, symbol: str, price: float, quantity: int, account_no: str) -> Dict[str, Any]:
        """
        Check if buying power is sufficient for an order.
        
        Args:
            symbol: Stock symbol
            price: Price per share
            quantity: Quantity to buy
            account_no: Account number
            
        Returns:
            Dictionary with buying power check results
        """
        try:
            buying_power_data = self.get_buying_power(account_no)
            available_power = buying_power_data.get('buyingPower', 0)
            
            total_cost = price * quantity
            can_buy = total_cost <= available_power
            max_quantity = self.get_max_buy_quantity(symbol, price, account_no)
            
            result = {
                'canBuy': can_buy,
                'totalCost': total_cost,
                'availableBuyingPower': available_power,
                'maxQuantity': max_quantity,
                'symbol': symbol,
                'price': price
            }
            
            return result
            
        except Exception as e:
            return {
                'canBuy': False,
                'totalCost': 0,
                'availableBuyingPower': 0,
                'maxQuantity': 0,
                'error': str(e),
                'symbol': symbol,
                'price': price
            }
    
    # Market Data Methods (Interface Implementation)
    def get_market_data(self, symbol: str) -> MarketData:
        """
        Get market data for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            MarketData object with current market information
        """
        try:
            # For now, use the stock price endpoint
            price_data = self.get_stock_price(symbol)
            
            return MarketData(
                symbol=symbol,
                price=price_data.get('price', 0),
                change=price_data.get('change', 0),
                change_percent=price_data.get('changePercent', 0),
                volume=price_data.get('volume', 0),
                high=price_data.get('high', 0),
                low=price_data.get('low', 0),
                open=price_data.get('open', 0),
                close=price_data.get('close', 0),
                bid=price_data.get('bid', 0),
                ask=price_data.get('ask', 0),
                timestamp=datetime.now()
            )
            
        except HTTPError as e:
            raise DNSEAPIError(f"Failed to get market data for {symbol}: HTTP {e.response.status_code}")
        except Exception as e:
            raise DNSEAPIError(f"Failed to get market data for {symbol}: {str(e)}")
    
    def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get current stock price and related information.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary containing price information
        """
        if not self.jwt_token:
            raise DNSEAPIError("Must authenticate first")
        
        try:
            url = f"{self.base_urls['order_service']}/market-data/{symbol}"
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'symbol': symbol,
                'price': data.get('price', 0),
                'change': data.get('change', 0),
                'changePercent': data.get('changePercent', 0),
                'volume': data.get('volume', 0),
                'high': data.get('high', 0),
                'low': data.get('low', 0),
                'open': data.get('open', 0),
                'close': data.get('close', 0),
                'bid': data.get('bid', 0),
                'ask': data.get('ask', 0),
                'bidVolume': 0,  # Not available in MarketData
                'askVolume': 0   # Not available in MarketData
            }
            
        except HTTPError as e:
            raise DNSEAPIError(f"Failed to get stock price for {symbol}: HTTP {e.response.status_code}")
        except Exception as e:
            raise DNSEAPIError(f"Failed to get stock price for {symbol}: {str(e)}")
    
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get stock information including lot size and price limits.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary containing stock information
        """
        if not self.jwt_token:
            raise DNSEAPIError("Must authenticate first")
        
        try:
            url = f"{self.base_urls['order_service']}/stock-info/{symbol}"
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'symbol': symbol,
                'lotSize': data.get('lotSize', 100),
                'ceilingPrice': data.get('ceilingPrice', 0),
                'floorPrice': data.get('floorPrice', 0),
                'referencePrice': data.get('referencePrice', 0),
                'exchange': data.get('exchange', 'HOSE'),
                'industry': data.get('industry', ''),
                'marketCap': data.get('marketCap', 0),
                'listedShares': data.get('listedShares', 0),
                'foreignLimit': data.get('foreignLimit', 0),
                'foreignOwnership': data.get('foreignOwnership', 0)
            }
            
        except HTTPError as e:
            raise DNSEAPIError(f"Failed to get stock info for {symbol}: HTTP {e.response.status_code}")
        except Exception as e:
            raise DNSEAPIError(f"Failed to get stock info for {symbol}: {str(e)}")
    
    def get_portfolio(self, account_no: str) -> Dict[str, Any]:
        """
        Get portfolio information for an account.
        
        Args:
            account_no: Account number
            
        Returns:
            Dictionary containing portfolio information
        """
        if not self.jwt_token:
            raise DNSEAPIError("Must authenticate first")
        
        try:
            url = f"{self.base_urls['order_service']}/portfolio/{account_no}"
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Calculate portfolio totals
            holdings = data.get('securities', [])
            total_market_value = 0
            total_cost = 0
            
            for holding in holdings:
                market_value = holding.get('marketValue', 0)
                cost_value = holding.get('costValue', 0)
                total_market_value += market_value
                total_cost += cost_value
            
            total_pnl = total_market_value - total_cost
            pnl_percent = (total_pnl / total_cost * 100) if total_cost > 0 else 0
            
            return {
                'accountNo': account_no,
                'totalMarketValue': total_market_value,
                'totalCostValue': total_cost,
                'totalPnL': total_pnl,
                'pnlPercent': pnl_percent,
                'cashBalance': data.get('cashBalance', 0),
                'buyingPower': data.get('buyingPower', 0),
                'securities': holdings,
                'asOfDate': data.get('asOfDate'),
                'currency': data.get('currency', 'VND')
            }
            
        except HTTPError as e:
            raise DNSEAPIError(f"Failed to get portfolio: HTTP {e.response.status_code}")
        except Exception as e:
            raise DNSEAPIError(f"Failed to get portfolio: {str(e)}")
    
    def get_orders(self, account_no: str) -> List[Dict[str, Any]]:
        """
        Get all orders for an account.
        
        Args:
            account_no: Account number
            
        Returns:
            List of order dictionaries with any status
        """
        if not self.jwt_token:
            raise DNSEAPIError("Must authenticate first")
        
        try:
            # According to DNSE docs, the endpoint for getting orders is:
            # https://api.dnse.com.vn/order-service/v2/orders?accountNo=<account>
            url = f"{self.base_urls['order_service']}/v2/orders"
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            params = {"accountNo": account_no}
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('orders', [])
            
        except HTTPError as e:
            raise DNSEAPIError(f"Failed to get orders: HTTP {e.response.status_code}")
        except Exception as e:
            raise DNSEAPIError(f"Failed to get orders: {str(e)}")
            
    def get_pending_orders(self, account_no: str) -> List[Dict[str, Any]]:
        """
        Get pending orders for an account.
        This is implemented using the get_orders method and filtering for pending status.
        
        Args:
            account_no: Account number
            
        Returns:
            List of pending order dictionaries
        """
        try:
            all_orders = self.get_orders(account_no)
            pending_statuses = ["pending", "pendingNew", "new", "partiallyFilled"]
            pending_orders = [order for order in all_orders if order.get("orderStatus") in pending_statuses]
            return pending_orders
            
        except Exception as e:
            raise DNSEAPIError(f"Failed to get pending orders: {str(e)}")
                
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except HTTPError as e:
            raise DNSEAPIError(f"Failed to get pending orders: HTTP {e.response.status_code}")
        except Exception as e:
            raise DNSEAPIError(f"Failed to get pending orders: {str(e)}")
    
    def cancel_order(self, order_id: str, account_no: str) -> Dict[str, Any]:
        """
        Cancel a pending order.
        
        Args:
            order_id: Order ID to cancel
            account_no: Account number
            
        Returns:
            Cancellation response dictionary
        """
        if not self.jwt_token or not self.trading_token:
            raise DNSEAPIError("Must have both JWT and trading tokens")
        
        try:
            url = f"{self.base_urls['order_service']}/orders/{order_id}"
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Trading-Token": self.trading_token
            }
            params = {"accountNo": account_no}
            
            response = requests.delete(url, headers=headers, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except HTTPError as e:
            error_msg = f"Failed to cancel order {order_id}: HTTP {e.response.status_code}"
            try:
                error_details = e.response.json()
                error_msg += f" - {error_details}"
            except (ValueError, KeyError):
                pass
            raise DNSEAPIError(error_msg)
        except Exception as e:
            raise DNSEAPIError(f"Failed to cancel order {order_id}: {str(e)}")
    
    def place_order(self, order_request: OrderRequest) -> Dict[str, Any]:
        """
        Place an order using the OrderRequest interface.
        
        Args:
            order_request: OrderRequest object containing order details
            
        Returns:
            Order placement response dictionary
        """
        if not self.jwt_token or not self.trading_token:
            raise DNSEAPIError("Must have both JWT and trading tokens")
        
        try:
            url = f"{self.base_urls['order_service']}/v2/orders"
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Trading-Token": self.trading_token,
                "Content-Type": "application/json"
            }
            
            # Convert enum values to API format
            side_mapping = {OrderSide.BUY: "NB", OrderSide.SELL: "NS"}
            type_mapping = {
                OrderType.LIMIT: "LO",
                OrderType.MARKET: "MP", 
                OrderType.ATO: "ATO",
                OrderType.ATC: "ATC"
            }
            
            payload = {
                "symbol": order_request.symbol,
                "side": side_mapping[order_request.side],
                "orderType": type_mapping[order_request.order_type],
                "price": order_request.price,
                "quantity": order_request.quantity,
                "accountNo": order_request.account_no
            }
            if order_request.loan_package_id is not None:
                payload["loanPackageId"] = order_request.loan_package_id
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            return response.json()
            
        except HTTPError as e:
            error_msg = f"Order placement failed: HTTP {e.response.status_code}"
            try:
                error_details = e.response.json()
                error_msg += f" - {error_details}"
            except (ValueError, KeyError):
                pass
            raise DNSEAPIError(error_msg)
        except Exception as e:
            raise DNSEAPIError(f"Order placement failed: {str(e)}")
    
    def get_order_details(self, order_id: str, account_no: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific order.
        
        Args:
            order_id: Order ID
            account_no: Account number
            
        Returns:
            Order details dictionary
        """
        if not self.jwt_token:
            raise DNSEAPIError("Must authenticate first")
        
        try:
            url = f"{self.base_urls['order_service']}/orders/{order_id}"
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            params = {"accountNo": account_no}
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except HTTPError as e:
            raise DNSEAPIError(f"Failed to get order details for {order_id}: HTTP {e.response.status_code}")
        except Exception as e:
            raise DNSEAPIError(f"Failed to get order details for {order_id}: {str(e)}")
    
    # Conditional Orders Methods
    def place_conditional_order(self, condition: str, target_order: dict, symbol: str, props: dict, account_no: str, category: str, time_in_force: dict) -> Dict[str, Any]:
        """
        Place a conditional order (lệnh điều kiện).
        Implements API: POST /conditional-order-api/v1/orders
        
        Args:
            condition: The price condition (e.g., "price >= 26650" or "price <= 26650")
            target_order: Dictionary with order details (quantity, side, price, loanPackageId, orderType)
            symbol: Stock symbol
            props: Dictionary with properties (stopPrice, marketId)
            account_no: Account number
            category: Order category (typically "STOP")
            time_in_force: Dictionary with time constraints (expireTime, kind)
            
        Returns:
            Dictionary with the order ID
        """
        if not self.jwt_token:
            raise DNSEAPIError("Must authenticate first")
        try:
            url = f"{self.base_urls['conditional_order_api']}/orders"
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "condition": condition,
                "targetOrder": target_order,
                "symbol": symbol,
                "props": props,
                "accountNo": account_no,
                "category": category,
                "timeInForce": time_in_force
            }
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            raise DNSEAPIError(f"Failed to place conditional order: HTTP {e.response.status_code}")
        except Exception as e:
            raise DNSEAPIError(f"Failed to place conditional order: {str(e)}")
    
    def get_conditional_orders(self, account_no: str, daily: bool = False, from_date: str = None, to_date: str = None, page: int = 1, size: int = 100, status: list = None, symbol: str = None, market_id: str = None) -> Dict[str, Any]:
        """
        Get list of conditional orders (sổ lệnh điều kiện).
        Implements API: GET /conditional-order-api/v1/orders
        
        Args:
            account_no: Account number
            daily: Whether to get only today's orders (default: False)
            from_date: Start date in format yyyy-MM-dd
            to_date: End date in format yyyy-MM-dd
            page: Page number for pagination
            size: Number of items per page
            status: List of order statuses (NEW/ACTIVATED/REJECTED/CANCELLED/EXPIRED/FAILED)
            symbol: Stock symbol filter
            market_id: Market ID filter (UNDERLYING for stocks, DERIVATIVES for derivatives)
            
        Returns:
            Dictionary with pagination information and list of conditional orders
        """
        if not self.jwt_token:
            raise DNSEAPIError("Must authenticate first")
        try:
            url = f"{self.base_urls['conditional_order_api']}/orders"
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            params = {"accountNo": account_no, "daily": str(daily).lower(), "page": page, "size": size}
            if from_date:
                params["from"] = from_date
            if to_date:
                params["to"] = to_date
            if status:
                params["status"] = status
            if symbol:
                params["symbol"] = symbol
            if market_id:
                params["marketId"] = market_id
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            raise DNSEAPIError(f"Failed to get conditional orders: HTTP {e.response.status_code}")
        except Exception as e:
            raise DNSEAPIError(f"Failed to get conditional orders: {str(e)}")
    
    def get_conditional_order_detail(self, order_id: str) -> Dict[str, Any]:
        """
        Get detail of a conditional order by ID.
        Implements API: GET /conditional-order-api/v1/orders/{id}
        
        Args:
            order_id: ID of the conditional order
            
        Returns:
            Dictionary with detailed conditional order information
        """
        if not self.jwt_token:
            raise DNSEAPIError("Must authenticate first")
        try:
            url = f"{self.base_urls['conditional_order_api']}/orders/{order_id}"
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            raise DNSEAPIError(f"Failed to get conditional order detail: HTTP {e.response.status_code}")
        except Exception as e:
            raise DNSEAPIError(f"Failed to get conditional order detail: {str(e)}")
    
    def cancel_conditional_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel a conditional order by ID.
        Implements API: PATCH /conditional-order-api/v1/orders/{id}/cancel
        
        Args:
            order_id: ID of the conditional order to cancel
            
        Returns:
            Dictionary with the cancelled order ID
        """
        if not self.jwt_token:
            raise DNSEAPIError("Must authenticate first")
        try:
            url = f"{self.base_urls['conditional_order_api']}/orders/{order_id}/cancel"
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            response = requests.patch(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            raise DNSEAPIError(f"Failed to cancel conditional order: HTTP {e.response.status_code}")
        except Exception as e:
            raise DNSEAPIError(f"Failed to cancel conditional order: {str(e)}")
    
    def get_order_book(self, account_no: str) -> Dict[str, Any]:
        """
        Get order book (sổ lệnh) for a specific account.
        Implements API: GET /order-service/v2/orders?accountNo=<account>
        """
        if not self.jwt_token:
            raise DNSEAPIError("Must authenticate first")
        try:
            url = f"{self.base_urls['order_service']}/v2/orders"
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            params = {"accountNo": account_no}
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            raise DNSEAPIError(f"Failed to get order book: HTTP {e.response.status_code}")
        except Exception as e:
            raise DNSEAPIError(f"Failed to get order book: {str(e)}")
    
    # Utility Methods
    def select_loan_package(self, loan_packages: List[Dict[str, Any]], prefer_non_margin: bool = True) -> Optional[Dict[str, Any]]:
        """
        Select an appropriate loan package from available packages.
        
        Args:
            loan_packages: List of available loan packages
            prefer_non_margin: Whether to prefer non-margin packages
            
        Returns:
            Selected loan package or None if none available
        """
        if not loan_packages:
            return None
        
        # Filter for active packages
        active_packages = [pkg for pkg in loan_packages if pkg.get('status') == 'ACTIVE']
        
        if not active_packages:
            return None
        
        if prefer_non_margin:
            # Look for non-margin packages first
            non_margin = [pkg for pkg in active_packages if not pkg.get('isMargin', True)]
            if non_margin:
                return non_margin[0]
        
        # Return first active package
        return active_packages[0]
    
    def is_authenticated(self) -> bool:
        """Check if client is authenticated with JWT token."""
        return self.jwt_token is not None
    
    def has_trading_token(self) -> bool:
        """Check if client has trading token for order placement."""
        return self.trading_token is not None
    
    # Convenience Methods
    def setup_trading_session(self, otp_code: str, account_index: int = 0) -> Dict[str, Any]:
        """
        Complete setup for a trading session (authenticate + OTP + get accounts/packages).
        
        Args:
            otp_code: OTP code from email
            account_index: Index of account to use (default: 0 for first account)
            
        Returns:
            Dictionary containing session information
            
        Raises:
            DNSEAPIError: If setup fails
        """
        # Step 1: Authenticate
        self.authenticate()
        
        # Step 2: Get investor info
        investor_info = self.get_investor_info()
        
        # Step 3: Get accounts
        accounts = self.get_accounts()
        if not accounts:
            raise DNSEAPIError("No trading accounts found")
        
        if account_index >= len(accounts):
            raise DNSEAPIError(f"Account index {account_index} out of range (found {len(accounts)} accounts)")
        
        selected_account = accounts[account_index]
        account_id = selected_account.get("id")
        
        # Step 4: Verify OTP and get trading token
        self.verify_otp_email(otp_code)
        
        # Step 5: Get loan packages for the selected account
        loan_packages = self.get_loan_packages(account_id)
        selected_package = self.select_loan_package(loan_packages)
        
        return {
            "investor_info": investor_info,
            "accounts": accounts,
            "selected_account": selected_account,
            "loan_packages": loan_packages,
            "selected_loan_package": selected_package,
            "jwt_token": self.jwt_token,
            "trading_token": self.trading_token
        }
    
    def quick_buy(self, symbol: str, price: float, quantity: float, 
                  account_index: int = 0, order_type: str = "LO") -> Dict[str, Any]:
        """
        Quick buy method for simplified order placement.
        
        Args:
            symbol: Stock symbol
            price: Buy price
            quantity: Quantity to buy
            account_index: Account index (default: 0)
            order_type: Order type ("LO", "MP", "ATO", "ATC")
            
        Returns:
            Order placement response
        """
        if not self.accounts:
            raise DNSEAPIError("No accounts available. Setup session first.")
        
        if account_index >= len(self.accounts):
            raise DNSEAPIError(f"Account index {account_index} out of range")
        
        account_id = self.accounts[account_index].get("id") or self.accounts[account_index].get("accountNo")
        
        # Get loan packages if not already loaded
        if not self.loan_packages:
            loan_packages = self.get_loan_packages(account_id)
        else:
            loan_packages = self.loan_packages
        
        selected_package = self.select_loan_package(loan_packages)
        
        loan_package_id = selected_package.get('id') if selected_package else None
        
        # Convert string order_type to enum
        order_type_enum = getattr(OrderType, order_type, OrderType.LIMIT)
        
        # Create OrderRequest object
        order_request = OrderRequest(
            symbol=symbol,
            side=OrderSide.BUY,
            order_type=order_type_enum,
            price=price,
            quantity=int(quantity),
            account_no=account_id,
            loan_package_id=loan_package_id
        )
        
        return self.place_order(order_request)
    
    def quick_sell(self, symbol: str, price: float, quantity: float, 
                   account_index: int = 0, order_type: str = "LO") -> Dict[str, Any]:
        """
        Quick sell method for simplified order placement.
        
        Args:
            symbol: Stock symbol
            price: Sell price
            quantity: Quantity to sell
            account_index: Account index (default: 0)
            order_type: Order type ("LO", "MP", "ATO", "ATC")
            
        Returns:
            Order placement response
        """
        if not self.accounts:
            raise DNSEAPIError("No accounts available. Setup session first.")
        
        if account_index >= len(self.accounts):
            raise DNSEAPIError(f"Account index {account_index} out of range")
        
        account_id = self.accounts[account_index].get("id") or self.accounts[account_index].get("accountNo")
        
        # Get loan packages if not already loaded
        if not self.loan_packages:
            loan_packages = self.get_loan_packages(account_id)
        else:
            loan_packages = self.loan_packages
        
        selected_package = self.select_loan_package(loan_packages)
        
        loan_package_id = selected_package.get('id') if selected_package else None
        
        # Convert string order_type to enum
        order_type_enum = getattr(OrderType, order_type, OrderType.LIMIT)
        
        # Create OrderRequest object
        order_request = OrderRequest(
            symbol=symbol,
            side=OrderSide.SELL,
            order_type=order_type_enum,
            price=price,
            quantity=int(quantity),
            account_no=account_id,
            loan_package_id=loan_package_id
        )
        
        return self.place_order(order_request)
    
    def create_stop_order(self, symbol: str, stop_price: float, order_price: float, 
                     quantity: int, side: OrderSide, account_no: str, 
                     loan_package_id: str = None, expire_time: str = None,
                     market_id: str = "UNDERLYING") -> Dict[str, Any]:
        """
        Convenience method to create a stop order (stop-loss or stop-buy).
        
        Args:
            symbol: Stock symbol
            stop_price: Trigger price
            order_price: Order price once triggered
            quantity: Order quantity
            side: OrderSide.BUY or OrderSide.SELL
            account_no: Account number
            loan_package_id: Optional loan package ID 
            expire_time: Order expiry time in format "YYYY-MM-DDThh:mm:ss.000Z", defaults to end of trading day
            market_id: Market ID ("UNDERLYING" for stocks, "DERIVATIVES" for derivatives)
            
        Returns:
            Order placement response dictionary
        """
        # Map the side enum to API values
        side_str = "NB" if side == OrderSide.BUY else "NS"
        
        # Set condition based on side
        if side == OrderSide.BUY:
            # For stop buy orders, execute when price rises above stop_price
            condition = f"price >= {stop_price}"
        else:
            # For stop sell (stop loss) orders, execute when price falls below stop_price
            condition = f"price <= {stop_price}"
        
        # Set default expiry time to end of current trading day if not provided
        if not expire_time:
            # Get current date in Vietnam time and set to 14:30 (market close)
            now = datetime.now()
            expire_time = f"{now.year}-{now.month:02d}-{now.day:02d}T07:30:00.000Z"  # UTC time (14:30 Vietnam time)
        
        # Create target order
        target_order = {
            "quantity": quantity,
            "side": side_str,
            "price": order_price,
            "orderType": "LO"
        }
        
        if loan_package_id:
            target_order["loanPackageId"] = loan_package_id
        
        # Properties
        props = {
            "stopPrice": stop_price,
            "marketId": market_id
        }
        
        # Time in force
        time_in_force = {
            "expireTime": expire_time,
            "kind": "GTD"  # Good Till Date
        }
        
        return self.place_conditional_order(
            condition=condition,
            target_order=target_order,
            symbol=symbol,
            props=props,
            account_no=account_no,
            category="STOP",
            time_in_force=time_in_force
        )

    def quick_stop_loss(self, symbol: str, stop_price: float, order_price: float, quantity: int,
                        account_index: int = 0, expire_time: str = None) -> Dict[str, Any]:
        """
        Quick method to place a stop-loss order.
        
        Args:
            symbol: Stock symbol
            stop_price: Price that triggers the stop-loss
            order_price: Sell price once triggered (usually same or slightly lower than stop_price)
            quantity: Quantity to sell
            account_index: Account index to use (default: 0)
            expire_time: Order expiry time (default: end of trading day)
            
        Returns:
            Conditional order placement response
        """
        if not self.accounts:
            raise DNSEAPIError("No accounts available. Setup session first.")
        
        if account_index >= len(self.accounts):
            raise DNSEAPIError(f"Account index {account_index} out of range")
        
        account_id = self.accounts[account_index].get("id") or self.accounts[account_index].get("accountNo")
        
        return self.create_stop_order(
            symbol=symbol,
            stop_price=stop_price,
            order_price=order_price,
            quantity=quantity,
            side=OrderSide.SELL,  # Stop-loss is a sell order
            account_no=account_id,
            expire_time=expire_time
        )

    def quick_take_profit(self, symbol: str, target_price: float, order_price: float, quantity: int,
                          account_index: int = 0, expire_time: str = None) -> Dict[str, Any]:
        """
        Quick method to place a take-profit order (sell when price reaches target).
        
        Args:
            symbol: Stock symbol
            target_price: Price that triggers the take-profit
            order_price: Sell price once triggered (usually same or slightly lower than target_price)
            quantity: Quantity to sell
            account_index: Account index to use (default: 0)
            expire_time: Order expiry time (default: end of trading day)
            
        Returns:
            Conditional order placement response
        """
        if not self.accounts:
            raise DNSEAPIError("No accounts available. Setup session first.")
        
        if account_index >= len(self.accounts):
            raise DNSEAPIError(f"Account index {account_index} out of range")
        
        account_id = self.accounts[account_index].get("id") or self.accounts[account_index].get("accountNo")
        
        # Take-profit is triggered when price rises above target
        condition = f"price >= {target_price}"
        
        target_order = {
            "quantity": quantity,
            "side": "NS",  # Take-profit is a sell order
            "price": order_price,
            "orderType": "LO"
        }
        
        # Set default expiry time if not provided
        if not expire_time:
            now = datetime.now()
            expire_time = f"{now.year}-{now.month:02d}-{now.day:02d}T07:30:00.000Z"  # UTC time (14:30 Vietnam time)
        
        # Properties
        props = {
            "stopPrice": target_price,
            "marketId": "UNDERLYING"
        }
        
        # Time in force
        time_in_force = {
            "expireTime": expire_time,
            "kind": "GTD"  # Good Till Date
        }
        
        return self.place_conditional_order(
            condition=condition,
            target_order=target_order,
            symbol=symbol,
            props=props,
            account_no=account_id,
            category="STOP",  # Even though it's take-profit, category is still "STOP"
            time_in_force=time_in_force
        )
