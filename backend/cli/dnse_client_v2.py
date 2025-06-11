# dnse_client.py
# A comprehensive Python client for the DNSE LightSpeed API.
#
# Author: Gemini
# Version: 1.1.0
#
# This client provides methods for authentication, account management,
# trading (equities and derivatives), deal management, risk management, conditional orders,
# and subscribing to real-time market data via MQTT over WebSockets.
#
# Required Libraries:
# pip install requests paho-mqtt

import requests
import json
import logging
import threading
import time
import os

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("paho-mqtt library not found. Please install it using: pip install paho-mqtt")
    exit()

# --- Configuration ---
# It's recommended to use environment variables for sensitive data.
# For example:
# export DNSE_USERNAME="your_username"
# export DNSE_PASSWORD="your_password"

# --- Constants ---
# Base URL for the DNSE RESTful Trading API
BASE_API_URL = "https://api.dnse.com.vn"

# Configuration for the Market Data WebSocket (MQTT)
MARKET_DATA_HOST = "datafeed-lts-krx.dnse.com.vn"
MARKET_DATA_PORT = 443
MARKET_DATA_PATH = "/wss"

# --- Logging Setup ---
# Sets up a logger for the client's activities.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DNSEClient:
    """
    A Python client for interacting with the DNSE LightSpeed API.

    This class handles authentication, session management, REST API calls for trading,
    and a WebSocket connection for real-time market data streams via MQTT.
    """

    def __init__(self, username, password):
        """
        Initializes the DNSEClient.

        Args:
            username (str): Your DNSE login username (email, phone, or custody code).
            password (str): Your DNSE login password.
        """
        if not username or not password:
            raise ValueError("Username and password must be provided.")

        self.username = username
        self.password = password
        self.session = requests.Session()  # Use a session for connection pooling and cookie persistence
        self.jwt_token = None
        self.trading_token = None
        self.investor_id = None
        self.account_info = {}

        # MQTT client for market data
        self._mqtt_client = None
        self._mqtt_thread = None
        self._is_mqtt_connected = threading.Event()
        self._mqtt_callbacks = {}  # topic -> callback function

    # --- Private Helper Methods ---

    def _make_request(self, method, endpoint, params=None, json_data=None, headers=None):
        """
        A centralized method for making HTTP requests to the DNSE API.
        """
        url = f"{BASE_API_URL}{endpoint}"
        try:
            response = self.session.request(
                method, url, params=params, json=json_data, headers=headers, timeout=15
            )
            response.raise_for_status()
            if response.text:
                return response.json()
            return {}
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err} - {http_err.response.text}")
            raise
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request exception occurred: {req_err}")
            raise

    def _get_auth_headers(self):
        """Returns headers for standard authenticated requests."""
        if not self.jwt_token:
            raise PermissionError("Not logged in. Please call login() first.")
        return {'Authorization': f'Bearer {self.jwt_token}', 'Content-Type': 'application/json'}

    def _get_trading_headers(self):
        """Returns headers for transactional requests (placing/canceling orders)."""
        if not self.jwt_token or not self.trading_token:
            raise PermissionError("Trading token not available. Please verify OTP first.")
        return {
            'Authorization': f'Bearer {self.jwt_token}',
            'trading-token': self.trading_token,
            'Content-Type': 'application/json'
        }

    # --- 1. Authentication Methods ---

    def login(self):
        """
        Logs into the DNSE platform to get a JWT token.
        """
        logger.info("Attempting to log in...")
        endpoint = "/auth-service/login"
        payload = {"username": self.username, "password": self.password}
        try:
            response = self._make_request('POST', endpoint, json_data=payload)
            self.jwt_token = response.get('token')
            if self.jwt_token:
                logger.info("Login successful. JWT token obtained.")
                self.get_user_info()
            else:
                logger.error("Login failed. No token in response.")
        except Exception as e:
            logger.error(f"An error occurred during login: {e}")
            raise

    def get_email_otp(self):
        """
        Requests an OTP to be sent to the registered email address.
        """
        logger.info("Requesting email OTP...")
        endpoint = "/auth-service/api/email-otp"
        try:
            self._make_request('GET', endpoint, headers=self._get_auth_headers())
            logger.info("Email OTP request sent successfully. Please check your email.")
        except Exception as e:
            logger.error(f"Failed to request email OTP: {e}")
            raise

    def verify_email_otp(self, otp_code):
        """
        Verifies the email OTP to obtain a trading token.
        """
        logger.info("Verifying email OTP to get trading token...")
        endpoint = "/order-service/trading-token"
        headers = self._get_auth_headers()
        headers['otp'] = otp_code
        try:
            response = self._make_request('POST', endpoint, headers=headers)
            self.trading_token = response.get('tradingToken')
            if self.trading_token:
                logger.info("Email OTP verified successfully. Trading token obtained.")
            else:
                logger.error("OTP verification failed. No trading token in response.")
        except Exception as e:
            logger.error(f"Failed to verify email OTP: {e}")
            raise
    
    def verify_smart_otp(self, smart_otp_code):
        """
        Verifies the Smart OTP from the Entrade X app to obtain a trading token.
        """
        logger.info("Verifying Smart OTP to get trading token...")
        endpoint = "/order-service/trading-token"
        headers = self._get_auth_headers()
        headers['smart-otp'] = smart_otp_code
        try:
            response = self._make_request('POST', endpoint, headers=headers)
            self.trading_token = response.get('tradingToken')
            if self.trading_token:
                logger.info("Smart OTP verified successfully. Trading token obtained.")
            else:
                logger.error("Smart OTP verification failed. No trading token in response.")
        except Exception as e:
            logger.error(f"Failed to verify Smart OTP: {e}")
            raise

    # --- 2. Account Information Methods ---

    def get_user_info(self):
        """Retrieves primary account details for the logged-in user."""
        logger.info("Fetching user information...")
        endpoint = "/user-service/api/me"
        try:
            self.account_info = self._make_request('GET', endpoint, headers=self._get_auth_headers())
            self.investor_id = self.account_info.get('investorId')
            logger.info(f"User information retrieved successfully for investor ID: {self.investor_id}")
            return self.account_info
        except Exception as e:
            logger.error(f"Failed to get user information: {e}")
            raise

    def get_sub_accounts(self):
        """Retrieves the list of trading sub-accounts."""
        logger.info("Fetching sub-accounts...")
        endpoint = "/order-service/accounts"
        try:
            return self._make_request('GET', endpoint, headers=self._get_auth_headers())
        except Exception as e:
            logger.error(f"Failed to get sub-accounts: {e}")
            raise

    def get_cash_balance(self, account):
        """
        Retrieves detailed cash balance information for a specific sub-account.
        """
        logger.info(f"Fetching cash balance for account: {account}...")
        endpoint = f"/order-service/account-balances/{account}"
        try:
            return self._make_request('GET', endpoint, headers=self._get_auth_headers())
        except Exception as e:
            logger.error(f"Failed to get cash balance for account {account}: {e}")
            raise

    # --- 3. Trading Methods (Equities & Derivatives) ---

    def get_loan_packages(self, account, derivative=False):
        """
        Get available margin loan packages for a sub-account.
        """
        endpoint_suffix = "derivative-loan-packages" if derivative else "loan-packages"
        logger.info(f"Fetching {'derivative' if derivative else 'equity'} loan packages for account: {account}...")
        endpoint = f"/order-service/accounts/{account}/{endpoint_suffix}"
        try:
            return self._make_request('GET', endpoint, headers=self._get_auth_headers())
        except Exception as e:
            logger.error(f"Failed to get loan packages: {e}")
            raise

    def get_buying_power(self, account, symbol, price, loan_package_id, derivative=False):
        """
        Calculates buying/selling power for a given symbol and price.
        """
        endpoint_suffix = "derivative-ppse" if derivative else "ppse"
        logger.info(f"Fetching buying power for {symbol} at price {price}...")
        endpoint = f"/order-service/accounts/{account}/{endpoint_suffix}"
        params = {"symbol": symbol, "price": price, "loanPackageId": loan_package_id}
        try:
            return self._make_request('GET', endpoint, params=params, headers=self._get_auth_headers())
        except Exception as e:
            logger.error(f"Failed to get buying power: {e}")
            raise

    def place_order(self, accountNo, symbol, side, orderType, quantity, price=None, loanPackageId=None, derivative=False):
        """
        Places a new order.
        """
        endpoint_suffix = "derivative/orders" if derivative else "v2/orders"
        logger.info(f"Placing {'derivative' if derivative else 'equity'} order: {side} {quantity} {symbol}@{price if price else orderType}")
        endpoint = f"/order-service/{endpoint_suffix}"
        payload = {"symbol": symbol, "side": side, "orderType": orderType, "quantity": quantity, "accountNo": accountNo}
        if price is not None: payload["price"] = price
        if loanPackageId is not None: payload["loanPackageId"] = loanPackageId
        try:
            return self._make_request('POST', endpoint, json_data=payload, headers=self._get_trading_headers())
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            raise

    def get_orders(self, account, derivative=False):
        """
        Retrieves the list of orders for a sub-account.
        """
        endpoint_suffix = "derivative/orders" if derivative else "v2/orders"
        logger.info(f"Fetching {'derivative' if derivative else 'equity'} order list for account {account}...")
        endpoint = f"/order-service/{endpoint_suffix}"
        params = {"accountNo": account}
        try:
            return self._make_request('GET', endpoint, params=params, headers=self._get_auth_headers())
        except Exception as e:
            logger.error(f"Failed to get orders: {e}")
            raise

    def get_order_details(self, order_id, account, derivative=False):
        """
        Retrieves details for a single order by its ID.
        """
        endpoint_suffix = "derivative/orders" if derivative else "v2/orders"
        logger.info(f"Fetching details for order ID: {order_id}...")
        endpoint = f"/order-service/{endpoint_suffix}/{order_id}"
        params = {"accountNo": account}
        try:
            return self._make_request('GET', endpoint, params=params, headers=self._get_auth_headers())
        except Exception as e:
            logger.error(f"Failed to get order details for {order_id}: {e}")
            raise

    def cancel_order(self, order_id, account, derivative=False):
        """
        Cancels an open order.
        """
        endpoint_suffix = "derivative/orders" if derivative else "v2/orders"
        logger.info(f"Cancelling order ID: {order_id}...")
        endpoint = f"/order-service/{endpoint_suffix}/{order_id}"
        params = {"accountNo": account}
        try:
            return self._make_request('DELETE', endpoint, params=params, headers=self._get_trading_headers())
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            raise

    # --- 4. Deal/Position Management ---

    def get_holding_deals(self, account, derivative=False):
        """
        Retrieves the list of currently held deals/positions.
        """
        service = "derivative-core" if derivative else "deal-service"
        logger.info(f"Fetching {'derivative' if derivative else 'equity'} holding deals for account {account}...")
        endpoint = f"/{service}/deals"
        params = {"accountNo": account}
        try:
            return self._make_request('GET', endpoint, params=params, headers=self._get_auth_headers())
        except Exception as e:
            logger.error(f"Failed to get holding deals: {e}")
            raise
    
    def close_derivative_deal(self, deal_id):
        """
        Closes a derivative deal.
        """
        logger.info(f"Closing derivative deal ID: {deal_id}...")
        endpoint = f"/derivative-core/deals/{deal_id}/close"
        try:
            return self._make_request('POST', endpoint, headers=self._get_trading_headers())
        except Exception as e:
            logger.error(f"Failed to close derivative deal {deal_id}: {e}")
            raise

    # --- 5. Derivatives Risk Management ---
    
    def configure_sl_tp_by_deal(self, deal_id, config_payload):
        """
        Sets stop-loss/take-profit parameters for a specific derivative deal.
        """
        logger.info(f"Configuring SL/TP for deal ID: {deal_id}...")
        endpoint = f"/derivative-deal-risk/pnl-configs/{deal_id}"
        try:
            return self._make_request('POST', endpoint, json_data=config_payload, headers=self._get_trading_headers())
        except Exception as e:
            logger.error(f"Failed to configure SL/TP for deal {deal_id}: {e}")
            raise

    def configure_sl_tp_by_account(self, account_no, config_payload):
        """
        Sets stop-loss/take-profit parameters for an entire derivative account.
        """
        logger.info(f"Configuring SL/TP for account: {account_no}...")
        endpoint = f"/derivative-deal-risk/account-pnl-configs/{account_no}"
        try:
            return self._make_request('PATCH', endpoint, json_data=config_payload, headers=self._get_trading_headers())
        except Exception as e:
            logger.error(f"Failed to configure SL/TP for account {account_no}: {e}")
            raise
    
    # --- 6. Conditional Orders ---
    
    def place_conditional_order(self, order_payload):
        """
        Places a new conditional order.
        """
        logger.info(f"Placing conditional order for symbol: {order_payload.get('symbol')}...")
        endpoint = "/conditional-order-api/v1/orders"
        try:
            # Note: The docs are ambiguous about the required token. Assuming trading-token for safety.
            return self._make_request('POST', endpoint, json_data=order_payload, headers=self._get_trading_headers())
        except Exception as e:
            logger.error(f"Failed to place conditional order: {e}")
            raise

    def get_conditional_orders(self, account_no, daily=False, from_date=None, to_date=None, status=None, symbol=None, market_id=None):
        """
        Retrieves a list of conditional orders.
        """
        logger.info(f"Fetching conditional orders for account: {account_no}...")
        endpoint = "/conditional-order-api/v1/orders"
        params = {"accountNo": account_no, "daily": daily}
        if from_date: params["from"] = from_date
        if to_date: params["to"] = to_date
        if status: params["status"] = status
        if symbol: params["symbol"] = symbol
        if market_id: params["marketId"] = market_id
        try:
            return self._make_request('GET', endpoint, params=params, headers=self._get_auth_headers())
        except Exception as e:
            logger.error(f"Failed to get conditional orders: {e}")
            raise

    def get_conditional_order_details(self, order_id):
        """
        Retrieves details for a single conditional order.
        """
        logger.info(f"Fetching details for conditional order ID: {order_id}...")
        endpoint = f"/conditional-order-api/v1/orders/{order_id}"
        try:
            return self._make_request('GET', endpoint, headers=self._get_auth_headers())
        except Exception as e:
            logger.error(f"Failed to get conditional order details for {order_id}: {e}")
            raise
            
    def cancel_conditional_order(self, order_id):
        """
        Cancels a conditional order.
        """
        logger.info(f"Cancelling conditional order ID: {order_id}...")
        endpoint = f"/conditional-order-api/v1/orders/{order_id}/cancel"
        try:
            # Assuming trading-token for safety.
            return self._make_request('PATCH', endpoint, headers=self._get_trading_headers())
        except Exception as e:
            logger.error(f"Failed to cancel conditional order {order_id}: {e}")
            raise

    # --- 7. Market Data (MQTT over WebSocket) Methods ---

    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """Callback for when the MQTT client connects."""
        if rc == 0:
            logger.info("Market Data client connected successfully.")
            self._is_mqtt_connected.set()
            for topic in self._mqtt_callbacks:
                logger.info(f"Resubscribing to topic: {topic}")
                self._mqtt_client.subscribe(topic)
        else:
            logger.error(f"Market Data client failed to connect, return code {rc}\n")

    def _on_mqtt_message(self, client, userdata, msg):
        """Callback for when a message is received from a subscribed topic."""
        try:
            payload = json.loads(msg.payload.decode())
            if msg.topic in self._mqtt_callbacks:
                self._mqtt_callbacks[msg.topic](msg.topic, payload)
        except json.JSONDecodeError:
            logger.warning(f"Could not decode JSON from message on topic {msg.topic}: {msg.payload}")
        except Exception as e:
            logger.error(f"Error in message callback for topic {msg.topic}: {e}")

    def _on_mqtt_disconnect(self, client, userdata, rc):
        """Callback for when the MQTT client disconnects."""
        self._is_mqtt_connected.clear()
        logger.warning(f"Market Data client disconnected (rc={rc}). Will attempt to reconnect if loop is running.")

    def _mqtt_loop(self):
        """The target function for the MQTT background thread."""
        while True:
            try:
                logger.info("Starting MQTT loop...")
                self._mqtt_client.loop_forever()
                break 
            except Exception as e:
                logger.error(f"Exception in MQTT loop: {e}. Reconnecting in 5 seconds...")
                time.sleep(5)

    def connect_market_data(self):
        """
        Connects to the real-time market data stream.
        """
        if not self.investor_id or not self.jwt_token:
            raise PermissionError("Cannot connect to market data. Please login() first.")
        if self._mqtt_client and self._is_mqtt_connected.is_set():
            logger.info("Market Data client is already connected.")
            return

        logger.info("Connecting to Market Data stream...")
        client_id = f"dnse_client_{self.investor_id}_{int(time.time())}"
        self._mqtt_client = mqtt.Client(client_id=client_id, transport="websockets")
        self._mqtt_client.ws_options_set(path=MARKET_DATA_PATH)
        self._mqtt_client.username_pw_set(username=self.investor_id, password=self.jwt_token)
        self._mqtt_client.on_connect = self._on_mqtt_connect
        self._mqtt_client.on_message = self._on_mqtt_message
        self._mqtt_client.on_disconnect = self._on_mqtt_disconnect
        self._mqtt_client.connect(MARKET_DATA_HOST, MARKET_DATA_PORT)

        self._mqtt_thread = threading.Thread(target=self._mqtt_loop, daemon=True)
        self._mqtt_thread.start()
        logger.info("Market Data connection process started in background.")

    def subscribe(self, topic, callback):
        """
        Subscribes to a market data topic.
        """
        if not self._mqtt_client:
            raise ConnectionError("Market Data client not connected. Call connect_market_data() first.")
        logger.info(f"Subscribing to topic: {topic}")
        self._mqtt_callbacks[topic] = callback
        if self._is_mqtt_connected.is_set():
            self._mqtt_client.subscribe(topic)

    def unsubscribe(self, topic):
        """Unsubscribes from a market data topic."""
        if not self._mqtt_client: return
        logger.info(f"Unsubscribing from topic: {topic}")
        if topic in self._mqtt_callbacks: del self._mqtt_callbacks[topic]
        if self._is_mqtt_connected.is_set(): self._mqtt_client.unsubscribe(topic)

    def disconnect_market_data(self):
        """Disconnects from the market data stream gracefully."""
        if self._mqtt_client:
            logger.info("Disconnecting from Market Data stream.")
            self._mqtt_client.loop_stop()
            self._mqtt_client.disconnect()
            self._is_mqtt_connected.clear()

# --- Example Usage ---
def example_market_data_callback(topic, payload):
    """A simple callback function to print received market data."""
    print(f"Callback received data for topic '{topic}': {json.dumps(payload, indent=2)}")

def main():
    """
    Main function to demonstrate the usage of the DNSEClient.
    """
    dnse_user = os.getenv("DNSE_USERNAME")
    dnse_pass = os.getenv("DNSE_PASSWORD")

    if not dnse_user or not dnse_pass:
        print("Please set DNSE_USERNAME and DNSE_PASSWORD environment variables.")
        return

    try:
        client = DNSEClient(username=dnse_user, password=dnse_pass)
        client.login()
        otp = input("Please enter the OTP sent to your email: ")
        client.verify_email_otp(otp)
        
        print("\n--- Getting Sub-Accounts ---")
        sub_accounts = client.get_sub_accounts()
        if sub_accounts and sub_accounts.get('accounts'):
            main_account = sub_accounts['accounts'][0]['id']
            print(f"Using main account: {main_account}")

            print("\n--- Getting Equity Holding Deals ---")
            deals = client.get_holding_deals(main_account)
            print(json.dumps(deals, indent=2))
            
            print("\n--- Placing a Conditional Order (Example) ---")
            cond_order_payload = {
              "condition": "price <= 26650",
              "targetOrder": {
                "quantity": 100,
                "side": "NB",
                "price": 26600,
                "loanPackageId": 1531, # Example ID, get from loan packages
                "orderType": "LO"
              },
              "symbol": "HPG",
              "props": {"stopPrice": 26650, "marketId": "UNDERLYING"},
              "accountNo": main_account,
              "category": "STOP",
              "timeInForce": {"expireTime": "2024-10-23T07:30:00.000Z", "kind": "GTD"}
            }
            # new_cond_order = client.place_conditional_order(cond_order_payload)
            # print(f"Placed new conditional order: {new_cond_order}")

            print("\n--- Getting Conditional Orders ---")
            all_cond_orders = client.get_conditional_orders(main_account, symbol="HPG")
            print(json.dumps(all_cond_orders, indent=2))

        else:
            print("No sub-accounts found.")

    except Exception as e:
        logger.error(f"An error occurred in the main execution block: {e}")
    finally:
        print("\n--- Example script finished ---")

if __name__ == "__main__":
    main()
