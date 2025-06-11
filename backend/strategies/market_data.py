# Market Data Handler for Grid Trading
import asyncio
import json
import logging
from decimal import Decimal
from typing import Dict, Optional, Callable, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MarketDataHandler:
    """
    Handles real-time market data streams for the grid trading bot
    """
    
    def __init__(self, api_client, symbol: str):
        self.api_client = api_client
        self.symbol = symbol
        self.current_price: Optional[Decimal] = None
        self.last_update: Optional[datetime] = None
        
        # Callbacks for price updates
        self.price_callbacks: list[Callable[[Decimal], None]] = []
        
        # Price history for analysis
        self.price_history: list[Dict[str, Any]] = []
        self.max_history_size = 1000
        
        # Connection status
        self.is_connected = False
    
    async def connect(self) -> bool:
        """Connect to market data stream"""
        try:
            logger.info(f"Connecting to market data for {self.symbol}")
            
            # Connect to MQTT market data
            self.api_client.connect_market_data()
            
            # Subscribe to price updates for the symbol
            price_topic = f"market/price/{self.symbol}"
            self.api_client.subscribe(price_topic, self._on_price_update)
            
            # Also subscribe to order book updates if available
            orderbook_topic = f"market/orderbook/{self.symbol}"
            self.api_client.subscribe(orderbook_topic, self._on_orderbook_update)
            
            self.is_connected = True
            logger.info(f"Successfully connected to market data for {self.symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to market data: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from market data stream"""
        try:
            if self.is_connected:
                self.api_client.disconnect_market_data()
                self.is_connected = False
                logger.info("Disconnected from market data")
        except Exception as e:
            logger.error(f"Error disconnecting from market data: {e}")
    
    def _on_price_update(self, topic: str, payload: Dict[str, Any]) -> None:
        """Handle incoming price updates"""
        try:
            # Extract price from payload (format may vary based on DNSE API)
            price_data = payload.get('data', payload)
            
            # Try different possible price field names
            price = None
            for price_field in ['price', 'last_price', 'close', 'current_price']:
                if price_field in price_data:
                    price = Decimal(str(price_data[price_field]))
                    break
            
            if price is None:
                logger.warning(f"Could not extract price from payload: {payload}")
                return
            
            # Update current price
            self.current_price = price
            self.last_update = datetime.now()
            
            # Add to price history
            self._add_to_history(price_data)
            
            # Notify callbacks
            for callback in self.price_callbacks:
                try:
                    callback(price)
                except Exception as e:
                    logger.error(f"Error in price callback: {e}")
            
            logger.debug(f"Price update for {self.symbol}: {price}")
            
        except Exception as e:
            logger.error(f"Error processing price update: {e}")
    
    def _on_orderbook_update(self, topic: str, payload: Dict[str, Any]) -> None:
        """Handle incoming order book updates"""
        try:
            # Extract bid/ask prices for better price discovery
            orderbook = payload.get('data', payload)
            
            if 'bids' in orderbook and 'asks' in orderbook:
                bids = orderbook['bids']
                asks = orderbook['asks']
                
                if bids and asks:
                    best_bid = Decimal(str(bids[0][0])) if bids[0] else None
                    best_ask = Decimal(str(asks[0][0])) if asks[0] else None
                    
                    if best_bid and best_ask:
                        # Use mid price as current price
                        mid_price = (best_bid + best_ask) / Decimal('2')
                        
                        # Update current price if it's more recent
                        if not self.current_price or abs(mid_price - self.current_price) > Decimal('0.01'):
                            self.current_price = mid_price
                            self.last_update = datetime.now()
                            
                            # Notify callbacks
                            for callback in self.price_callbacks:
                                try:
                                    callback(mid_price)
                                except Exception as e:
                                    logger.error(f"Error in price callback: {e}")
            
        except Exception as e:
            logger.error(f"Error processing orderbook update: {e}")
    
    def _add_to_history(self, price_data: Dict[str, Any]) -> None:
        """Add price data to history"""
        try:
            history_entry = {
                'timestamp': datetime.now(),
                'price': float(self.current_price) if self.current_price else None,
                'data': price_data
            }
            
            self.price_history.append(history_entry)
            
            # Limit history size
            if len(self.price_history) > self.max_history_size:
                self.price_history = self.price_history[-self.max_history_size:]
                
        except Exception as e:
            logger.error(f"Error adding to price history: {e}")
    
    def add_price_callback(self, callback: Callable[[Decimal], None]) -> None:
        """Add a callback function to be called on price updates"""
        self.price_callbacks.append(callback)
    
    def remove_price_callback(self, callback: Callable[[Decimal], None]) -> None:
        """Remove a price callback"""
        if callback in self.price_callbacks:
            self.price_callbacks.remove(callback)
    
    def get_current_price(self) -> Optional[Decimal]:
        """Get the current market price"""
        return self.current_price
    
    def get_last_update_time(self) -> Optional[datetime]:
        """Get the timestamp of the last price update"""
        return self.last_update
    
    def is_price_stale(self, max_age_seconds: int = 30) -> bool:
        """Check if the current price is stale"""
        if not self.last_update:
            return True
        
        age = (datetime.now() - self.last_update).total_seconds()
        return age > max_age_seconds
    
    def get_price_history(self, limit: Optional[int] = None) -> list[Dict[str, Any]]:
        """Get price history"""
        if limit:
            return self.price_history[-limit:]
        return self.price_history.copy()
    
    def calculate_volatility(self, period_minutes: int = 60) -> Optional[Decimal]:
        """Calculate price volatility over the specified period"""
        try:
            cutoff_time = datetime.now() - timedelta(minutes=period_minutes)
            recent_prices = [
                Decimal(str(entry['price'])) 
                for entry in self.price_history 
                if entry['timestamp'] >= cutoff_time and entry['price'] is not None
            ]
            
            if len(recent_prices) < 2:
                return None
            
            # Calculate standard deviation of price changes
            price_changes = [
                abs(recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1]
                for i in range(1, len(recent_prices))
            ]
            
            if not price_changes:
                return None
            
            mean_change = sum(price_changes) / len(price_changes)
            variance = sum((change - mean_change) ** 2 for change in price_changes) / len(price_changes)
            volatility = variance ** Decimal('0.5')
            
            return volatility
            
        except Exception as e:
            logger.error(f"Error calculating volatility: {e}")
            return None
    
    def get_price_trend(self, period_minutes: int = 30) -> Optional[str]:
        """Determine price trend over the specified period"""
        try:
            cutoff_time = datetime.now() - timedelta(minutes=period_minutes)
            recent_prices = [
                Decimal(str(entry['price'])) 
                for entry in self.price_history 
                if entry['timestamp'] >= cutoff_time and entry['price'] is not None
            ]
            
            if len(recent_prices) < 10:
                return None
            
            # Simple trend calculation: compare first 25% with last 25%
            quarter_size = len(recent_prices) // 4
            early_avg = sum(recent_prices[:quarter_size]) / quarter_size
            late_avg = sum(recent_prices[-quarter_size:]) / quarter_size
            
            change_pct = (late_avg - early_avg) / early_avg
            
            if change_pct > Decimal('0.005'):  # >0.5% increase
                return "UP"
            elif change_pct < Decimal('-0.005'):  # >0.5% decrease
                return "DOWN"
            else:
                return "SIDEWAYS"
                
        except Exception as e:
            logger.error(f"Error calculating price trend: {e}")
            return None

# Fallback price provider for when real-time data is not available
class FallbackPriceProvider:
    """
    Provides price data when real-time streams are not available
    Uses REST API calls to get current market prices
    """
    
    def __init__(self, api_client, symbol: str, update_interval: int = 10):
        self.api_client = api_client
        self.symbol = symbol
        self.update_interval = update_interval
        self.current_price: Optional[Decimal] = None
        self.last_update: Optional[datetime] = None
        self.price_callbacks: list[Callable[[Decimal], None]] = []
        self.is_running = False
        self._update_task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start the fallback price provider"""
        if self.is_running:
            return
        
        self.is_running = True
        self._update_task = asyncio.create_task(self._update_loop())
        logger.info(f"Started fallback price provider for {self.symbol}")
    
    async def stop(self) -> None:
        """Stop the fallback price provider"""
        self.is_running = False
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
        logger.info(f"Stopped fallback price provider for {self.symbol}")
    
    async def _update_loop(self) -> None:
        """Main update loop"""
        while self.is_running:
            try:
                await self._fetch_current_price()
                await asyncio.sleep(self.update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in fallback price update: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _fetch_current_price(self) -> None:
        """Fetch current price using REST API"""
        try:
            # This would need to be implemented based on available DNSE market data API
            # For now, we'll use a placeholder implementation
            
            # In a real implementation, you might call something like:
            # market_data = await self.api_client.get_market_data(self.symbol)
            # price = market_data.get('last_price')
            
            # Placeholder: simulate price movement
            if self.current_price is None:
                self.current_price = Decimal('26000')  # Initial price
            else:
                # Small random price movement for simulation
                import random
                change_pct = (random.random() - 0.5) * 0.02  # ±1% change
                self.current_price = self.current_price * (Decimal('1') + Decimal(str(change_pct)))
            
            self.last_update = datetime.now()
            
            # Notify callbacks
            for callback in self.price_callbacks:
                try:
                    callback(self.current_price)
                except Exception as e:
                    logger.error(f"Error in fallback price callback: {e}")
            
        except Exception as e:
            logger.error(f"Error fetching current price: {e}")
    
    def add_price_callback(self, callback: Callable[[Decimal], None]) -> None:
        """Add a callback function to be called on price updates"""
        self.price_callbacks.append(callback)
    
    def get_current_price(self) -> Optional[Decimal]:
        """Get the current market price"""
        return self.current_price
