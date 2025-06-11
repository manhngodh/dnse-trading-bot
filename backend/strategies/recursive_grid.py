# Recursive Grid Trading Implementation
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal
from datetime import datetime
import logging
import asyncio

from .grid_base import (
    GridLevel, GridPosition, GridConfig, EMASmoother, 
    PriceUtils, RiskManager
)
from .market_data import MarketDataHandler, FallbackPriceProvider

logger = logging.getLogger(__name__)

class RecursiveGridStrategy:
    """
    Recursive Grid Trading Strategy Implementation
    
    Based on Passivbot's recursive grid mode where each subsequent reentry node
    is calculated as if the previous node had just been filled.
    """
    
    def __init__(self, config: GridConfig, api_client):
        self.config = config
        self.api_client = api_client
        
        # Validate configuration
        config_errors = config.validate()
        if config_errors:
            raise ValueError(f"Invalid configuration: {', '.join(config_errors)}")
        
        # Initialize components
        self.position = GridPosition(symbol=config.symbol)
        self.risk_manager = RiskManager(config)
        self.ema_smoother = EMASmoother(config.ema_span_0, config.ema_span_1) if config.use_ema_smoothing else None
        
        # Market data handler
        self.market_data_handler = MarketDataHandler(api_client, config.symbol)
        self.fallback_provider = FallbackPriceProvider(api_client, config.symbol)
        
        # Grid state
        self.grid_levels: Dict[str, GridLevel] = {}  # order_id -> GridLevel
        self.current_market_price: Optional[Decimal] = None
        self.is_active = False
        self.initial_capital: Optional[Decimal] = None
        
        # Performance tracking
        self.trade_history: List[Dict] = []
        self.start_time: Optional[datetime] = None
        
    async def initialize(self) -> bool:
        """Initialize the strategy with current market data and account info"""
        try:
            logger.info(f"Initializing Recursive Grid Strategy for {self.config.symbol}")
            
            # Initialize market data handler
            self.market_data_handler.add_price_callback(self._on_price_update)
            if not await self.market_data_handler.connect():
                logger.warning("Failed to connect to real-time market data, using fallback")
                self.fallback_provider.add_price_callback(self._on_price_update)
                await self.fallback_provider.start()
            
            # Get account balance
            balance_info = await self._get_account_balance()
            if not balance_info:
                logger.error("Failed to get account balance")
                return False
            
            self.initial_capital = Decimal(str(balance_info.get('available_cash', 0)))
            logger.info(f"Initial capital: {self.initial_capital:,.0f} VND")
            
            # Get current market price
            market_price = await self._get_current_price()
            if not market_price:
                logger.error("Failed to get current market price")
                return False
                
            self.current_market_price = market_price
            logger.info(f"Current market price: {self.current_market_price:,.0f}")
            
            # Initialize EMA smoother if enabled
            if self.ema_smoother:
                self.ema_smoother.add_price(self.current_market_price)
            
            self.start_time = datetime.now()
            self.is_active = True
            
            logger.info("Strategy initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize strategy: {e}")
            return False
    
    async def start_trading(self) -> None:
        """Start the grid trading process"""
        if not self.is_active:
            logger.error("Strategy not initialized. Call initialize() first.")
            return
        
        logger.info("Starting recursive grid trading...")
        
        # Place initial grid orders
        await self._place_initial_grid()
        
        # Start monitoring loop
        await self._monitoring_loop()
    
    async def stop_trading(self) -> None:
        """Stop trading and cancel all open orders"""
        logger.info("Stopping grid trading...")
        self.is_active = False
        
        # Cancel all open orders
        await self._cancel_all_orders()
        
        # Disconnect market data
        self.market_data_handler.disconnect()
        await self.fallback_provider.stop()
        
        # Log final performance
        await self._log_performance_summary()
    
    def _on_price_update(self, price: Decimal) -> None:
        """Callback for market price updates"""
        try:
            self.current_market_price = price
            
            # Update EMA if enabled
            if self.ema_smoother:
                self.ema_smoother.add_price(price)
            
            # Update unrealized PnL
            if self.position.total_quantity > 0 and self.position.average_price > 0:
                self.position.unrealized_pnl = (price - self.position.average_price) * Decimal(str(self.position.total_quantity))
            
        except Exception as e:
            logger.error(f"Error processing price update: {e}")
    
    async def _place_initial_grid(self) -> None:
        """Place the initial grid of buy orders"""
        if not self.current_market_price:
            logger.error("No market price available")
            return
        
        try:
            # Calculate initial grid levels (buy orders below current price)
            grid_prices = self._calculate_recursive_grid_levels(
                self.current_market_price, 
                is_initial=True
            )
            
            for i, price in enumerate(grid_prices):
                # Calculate quantity for this level
                quantity = self._calculate_order_quantity(price, i)
                
                if quantity > 0:
                    # Check risk limits
                    if not self._check_risk_limits(quantity, price):
                        logger.warning(f"Risk limits exceeded for level {i} at price {price}")
                        continue
                    
                    # Place buy order
                    order_result = await self._place_limit_order(
                        side='NB',  # Net Buy for DNSE
                        quantity=quantity,
                        price=price
                    )
                    
                    if order_result and order_result.get('orderId'):
                        # Track this grid level
                        grid_level = GridLevel(
                            price=price,
                            quantity=quantity,
                            side='BUY',
                            order_id=order_result['orderId'],
                            grid_index=i
                        )
                        self.grid_levels[order_result['orderId']] = grid_level
                        
                        logger.info(f"Placed buy order: {quantity} @ {price:,.0f} (Order ID: {order_result['orderId']})")
                    else:
                        logger.error(f"Failed to place buy order at {price}")
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error placing initial grid: {e}")
    
    def _calculate_recursive_grid_levels(self, reference_price: Decimal, 
                                       is_initial: bool = False) -> List[Decimal]:
        """Calculate grid levels recursively"""
        levels = []
        current_price = reference_price
        
        # For initial grid, place buy orders below current price
        if is_initial:
            for i in range(self.config.grid_levels):
                # Each level is calculated based on the previous level
                level_price = current_price * (Decimal('1') - self.config.grid_spacing_pct)
                level_price = PriceUtils.round_price(level_price, self.config.price_precision)
                levels.append(level_price)
                current_price = level_price
        else:
            # For reentry calculation, start from current average price or reference
            avg_price = self.position.average_price if self.position.average_price > 0 else reference_price
            current_price = avg_price
            
            # Calculate remaining grid levels below average price
            remaining_levels = max(0, self.config.grid_levels - len(self.grid_levels))
            for i in range(remaining_levels):
                level_price = current_price * (Decimal('1') - self.config.grid_spacing_pct)
                level_price = PriceUtils.round_price(level_price, self.config.price_precision)
                levels.append(level_price)
                current_price = level_price
        
        return levels
    
    def _calculate_order_quantity(self, price: Decimal, grid_index: int) -> int:
        """Calculate order quantity using DCA progression"""
        if not self.initial_capital:
            return 0
        
        # Base quantity percentage
        base_qty_pct = self.config.initial_qty_pct
        
        # Apply DCA factor for deeper levels
        dca_multiplier = self.config.ddown_factor ** grid_index
        adjusted_qty_pct = base_qty_pct * dca_multiplier
        
        # Calculate quantity
        quantity = PriceUtils.calculate_quantity_for_price(
            self.initial_capital,
            price,
            adjusted_qty_pct,
            self.config.min_order_value
        )
        
        return quantity
    
    def _check_risk_limits(self, quantity: int, price: Decimal) -> bool:
        """Check if order passes risk management rules"""
        # Check maximum position size
        if not self.risk_manager.check_max_position_size(self.position.total_quantity, quantity):
            return False
        
        # Check wallet exposure
        additional_value = Decimal(str(quantity)) * price
        current_value = Decimal(str(self.position.total_quantity)) * self.current_market_price if self.current_market_price else Decimal('0')
        total_value = current_value + additional_value
        
        if self.initial_capital:
            return self.risk_manager.check_wallet_exposure(total_value, self.initial_capital)
        
        return True
    
    async def _place_limit_order(self, side: str, quantity: int, price: Decimal) -> Optional[Dict]:
        """Place a limit order through the API"""
        try:
            order_payload = {
                'accountNo': self.config.account_no,
                'symbol': self.config.symbol,
                'side': side,
                'orderType': 'LO',  # Limit Order
                'quantity': quantity,
                'price': float(price)
            }
            
            if self.config.loan_package_id:
                order_payload['loanPackageId'] = self.config.loan_package_id
            
            result = await self._call_api_async(
                self.api_client.place_order,
                **order_payload
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error placing limit order: {e}")
            return None
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop for order fills and market updates"""
        logger.info("Starting monitoring loop...")
        
        while self.is_active:
            try:
                # Check for order fills
                await self._check_order_fills()
                
                # Update market price
                await self._update_market_price()
                
                # Check if we need to place new orders
                await self._manage_grid_orders()
                
                # Check risk limits and stop conditions
                if await self._check_stop_conditions():
                    logger.warning("Stop conditions met, halting strategy")
                    break
                
                # Wait before next iteration
                await asyncio.sleep(5)  # 5-second monitoring interval
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10)  # Longer wait on error
    
    async def _check_order_fills(self) -> None:
        """Check for filled orders and handle them"""
        try:
            # Get current orders
            orders = await self._call_api_async(
                self.api_client.get_orders,
                self.config.account_no
            )
            
            if not orders or 'orders' not in orders:
                return
            
            for order in orders['orders']:
                order_id = order.get('orderId')
                if order_id in self.grid_levels:
                    grid_level = self.grid_levels[order_id]
                    
                    # Check if order is filled
                    if order.get('status') in ['FILLED', 'PARTIALLY_FILLED']:
                        filled_qty = order.get('executedQuantity', 0)
                        fill_price = Decimal(str(order.get('averagePrice', grid_level.price)))
                        
                        if filled_qty > 0 and not grid_level.is_filled:
                            await self._handle_order_fill(grid_level, filled_qty, fill_price)
                            
        except Exception as e:
            logger.error(f"Error checking order fills: {e}")
    
    async def _handle_order_fill(self, grid_level: GridLevel, filled_qty: int, fill_price: Decimal) -> None:
        """Handle when a grid order is filled"""
        try:
            logger.info(f"Order filled: {filled_qty} @ {fill_price:,.0f} (Grid level {grid_level.grid_index})")
            
            # Update position
            self.position.update_position(filled_qty, fill_price, grid_level.side)
            
            # Mark grid level as filled
            grid_level.is_filled = True
            grid_level.filled_time = datetime.now()
            
            # Record trade
            trade_record = {
                'timestamp': datetime.now(),
                'symbol': self.config.symbol,
                'side': grid_level.side,
                'quantity': filled_qty,
                'price': fill_price,
                'grid_index': grid_level.grid_index,
                'order_id': grid_level.order_id
            }
            self.trade_history.append(trade_record)
            
            # Place take profit order if we bought
            if grid_level.side == 'BUY':
                await self._place_take_profit_order(filled_qty, fill_price)
            
            # Place new grid order to replace the filled one
            await self._place_replacement_grid_order(grid_level)
            
            # Update performance metrics
            await self._update_performance_metrics()
            
        except Exception as e:
            logger.error(f"Error handling order fill: {e}")
    
    async def _place_take_profit_order(self, quantity: int, cost_price: Decimal) -> None:
        """Place a take profit sell order"""
        try:
            # Calculate take profit price
            markup_pct = self.config.min_markup_pct + (
                self.config.markup_range_pct * (Decimal(str(self.position.total_quantity)) / Decimal(str(self.config.max_position_size)))
            )
            
            tp_price = cost_price * (Decimal('1') + markup_pct)
            tp_price = PriceUtils.round_price(tp_price, self.config.price_precision)
            
            # Place sell order
            order_result = await self._place_limit_order(
                side='NS',  # Net Sell for DNSE
                quantity=quantity,
                price=tp_price
            )
            
            if order_result and order_result.get('orderId'):
                # Track as sell grid level
                grid_level = GridLevel(
                    price=tp_price,
                    quantity=quantity,
                    side='SELL',
                    order_id=order_result['orderId'],
                    grid_index=-1  # TP orders use negative index
                )
                self.grid_levels[order_result['orderId']] = grid_level
                
                logger.info(f"Placed take profit order: {quantity} @ {tp_price:,.0f}")
            
        except Exception as e:
            logger.error(f"Error placing take profit order: {e}")
    
    async def _place_replacement_grid_order(self, filled_level: GridLevel) -> None:
        """Place a new grid order to replace the filled one"""
        try:
            # Calculate new grid level price recursively
            new_levels = self._calculate_recursive_grid_levels(
                self.position.average_price if self.position.average_price > 0 else self.current_market_price
            )
            
            if new_levels:
                # Take the deepest level that's not already covered
                new_price = new_levels[-1]
                
                # Calculate quantity for new level
                quantity = self._calculate_order_quantity(new_price, filled_level.grid_index + 1)
                
                if quantity > 0 and self._check_risk_limits(quantity, new_price):
                    order_result = await self._place_limit_order(
                        side='NB',
                        quantity=quantity,
                        price=new_price
                    )
                    
                    if order_result and order_result.get('orderId'):
                        grid_level = GridLevel(
                            price=new_price,
                            quantity=quantity,
                            side='BUY',
                            order_id=order_result['orderId'],
                            grid_index=filled_level.grid_index + 1
                        )
                        self.grid_levels[order_result['orderId']] = grid_level
                        
                        logger.info(f"Placed replacement grid order: {quantity} @ {new_price:,.0f}")
            
        except Exception as e:
            logger.error(f"Error placing replacement grid order: {e}")
    
    async def _update_market_price(self) -> None:
        """Update current market price"""
        try:
            price = await self._get_current_price()
            if price:
                self.current_market_price = price
                
                # Update EMA if enabled
                if self.ema_smoother:
                    self.ema_smoother.add_price(price)
                
                # Update unrealized PnL
                if self.position.total_quantity > 0 and self.position.average_price > 0:
                    self.position.unrealized_pnl = (price - self.position.average_price) * Decimal(str(self.position.total_quantity))
                    
        except Exception as e:
            logger.error(f"Error updating market price: {e}")
    
    async def _manage_grid_orders(self) -> None:
        """Manage grid orders - cancel outdated ones, place new ones if needed"""
        try:
            # Remove filled orders from tracking
            filled_orders = [oid for oid, level in self.grid_levels.items() if level.is_filled]
            for order_id in filled_orders:
                del self.grid_levels[order_id]
            
            # Check if we need more buy orders
            active_buy_orders = len([level for level in self.grid_levels.values() if level.side == 'BUY'])
            
            if active_buy_orders < self.config.grid_levels // 2:  # Maintain at least half the grid
                await self._add_grid_orders()
                
        except Exception as e:
            logger.error(f"Error managing grid orders: {e}")
    
    async def _add_grid_orders(self) -> None:
        """Add additional grid orders if needed"""
        try:
            # Calculate how many orders we need
            current_buy_orders = len([level for level in self.grid_levels.values() if level.side == 'BUY'])
            orders_needed = self.config.grid_levels - current_buy_orders
            
            if orders_needed > 0:
                # Calculate new grid levels
                reference_price = self.position.average_price if self.position.average_price > 0 else self.current_market_price
                new_levels = self._calculate_recursive_grid_levels(reference_price)
                
                # Get existing price levels to avoid duplicates
                existing_prices = {level.price for level in self.grid_levels.values() if level.side == 'BUY'}
                
                orders_placed = 0
                for i, price in enumerate(new_levels):
                    if orders_placed >= orders_needed:
                        break
                        
                    if price not in existing_prices:
                        quantity = self._calculate_order_quantity(price, len(self.grid_levels) + i)
                        
                        if quantity > 0 and self._check_risk_limits(quantity, price):
                            order_result = await self._place_limit_order('NB', quantity, price)
                            
                            if order_result and order_result.get('orderId'):
                                grid_level = GridLevel(
                                    price=price,
                                    quantity=quantity,
                                    side='BUY',
                                    order_id=order_result['orderId'],
                                    grid_index=len(self.grid_levels)
                                )
                                self.grid_levels[order_result['orderId']] = grid_level
                                orders_placed += 1
                                
                                logger.info(f"Added grid order: {quantity} @ {price:,.0f}")
                        
                        await asyncio.sleep(0.1)  # Rate limiting
                        
        except Exception as e:
            logger.error(f"Error adding grid orders: {e}")
    
    async def _check_stop_conditions(self) -> bool:
        """Check if trading should be stopped"""
        try:
            # Check drawdown limit
            if self.initial_capital:
                total_pnl = self.position.realized_pnl + self.position.unrealized_pnl
                if self.risk_manager.should_stop_trading(total_pnl, self.initial_capital):
                    logger.warning(f"Maximum drawdown exceeded: {total_pnl}")
                    return True
            
            # Check stop loss
            if self.config.stop_loss_pct and self.position.average_price > 0:
                stop_price = self.risk_manager.calculate_stop_loss_price(self.position.average_price)
                if stop_price and self.current_market_price and self.current_market_price <= stop_price:
                    logger.warning(f"Stop loss triggered at {self.current_market_price}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking stop conditions: {e}")
            return False
    
    async def _cancel_all_orders(self) -> None:
        """Cancel all active grid orders"""
        try:
            for order_id, grid_level in self.grid_levels.items():
                if not grid_level.is_filled:
                    await self._call_api_async(
                        self.api_client.cancel_order,
                        order_id,
                        self.config.account_no
                    )
                    logger.info(f"Cancelled order: {order_id}")
                    
        except Exception as e:
            logger.error(f"Error cancelling orders: {e}")
    
    async def _get_current_price(self) -> Optional[Decimal]:
        """Get current market price for the symbol"""
        try:
            # Try to get from market data handler first
            price = self.market_data_handler.get_current_price()
            if price:
                return price
            
            # Try fallback provider
            price = self.fallback_provider.get_current_price()
            if price:
                return price
            
            # If both fail, try to get from API (placeholder implementation)
            # This would need actual market data API endpoint
            logger.warning("No market data available, using placeholder price")
            return Decimal('26000')  # Placeholder
            
        except Exception as e:
            logger.error(f"Error getting current price: {e}")
            return None
    
    async def _get_account_balance(self) -> Optional[Dict]:
        """Get account balance information"""
        try:
            balance = await self._call_api_async(
                self.api_client.get_cash_balance,
                self.config.account_no
            )
            return balance
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            return None
    
    async def _call_api_async(self, func, *args, **kwargs):
        """Call synchronous API function asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)
    
    async def _update_performance_metrics(self) -> None:
        """Update and log performance metrics"""
        try:
            if not self.start_time:
                return
            
            total_pnl = self.position.realized_pnl + self.position.unrealized_pnl
            total_trades = len(self.trade_history)
            
            if total_trades > 0:
                win_trades = len([t for t in self.trade_history if t.get('pnl', 0) > 0])
                win_rate = win_trades / total_trades if total_trades > 0 else 0
                
                logger.info(f"Performance Update - Total PnL: {total_pnl:,.0f}, "
                          f"Trades: {total_trades}, Win Rate: {win_rate:.1%}")
                          
        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")
    
    async def _log_performance_summary(self) -> None:
        """Log final performance summary"""
        try:
            total_pnl = self.position.realized_pnl + self.position.unrealized_pnl
            duration = datetime.now() - self.start_time if self.start_time else None
            
            logger.info("=== GRID TRADING PERFORMANCE SUMMARY ===")
            logger.info(f"Symbol: {self.config.symbol}")
            logger.info(f"Duration: {duration}")
            logger.info(f"Total Trades: {len(self.trade_history)}")
            logger.info(f"Final Position: {self.position.total_quantity} shares")
            logger.info(f"Average Price: {self.position.average_price:,.0f}")
            logger.info(f"Realized PnL: {self.position.realized_pnl:,.0f}")
            logger.info(f"Unrealized PnL: {self.position.unrealized_pnl:,.0f}")
            logger.info(f"Total PnL: {total_pnl:,.0f}")
            if self.initial_capital:
                roi = (total_pnl / self.initial_capital) * 100
                logger.info(f"ROI: {roi:.2f}%")
            logger.info("========================================")
            
        except Exception as e:
            logger.error(f"Error logging performance summary: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current strategy status"""
        return {
            'is_active': self.is_active,
            'symbol': self.config.symbol,
            'position': {
                'quantity': self.position.total_quantity,
                'average_price': float(self.position.average_price),
                'unrealized_pnl': float(self.position.unrealized_pnl),
                'realized_pnl': float(self.position.realized_pnl)
            },
            'grid_orders': len(self.grid_levels),
            'active_buy_orders': len([level for level in self.grid_levels.values() if level.side == 'BUY' and not level.is_filled]),
            'active_sell_orders': len([level for level in self.grid_levels.values() if level.side == 'SELL' and not level.is_filled]),
            'total_trades': len(self.trade_history),
            'current_price': float(self.current_market_price) if self.current_market_price else None
        }
