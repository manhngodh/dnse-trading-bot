# Core grid trading base classes and utilities
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import math
import logging

logger = logging.getLogger(__name__)

@dataclass
class GridLevel:
    """Represents a single level in the grid"""
    price: Decimal
    quantity: int
    side: str  # 'BUY' or 'SELL'
    order_id: Optional[str] = None
    is_filled: bool = False
    filled_time: Optional[datetime] = None
    grid_index: int = 0

@dataclass
class GridPosition:
    """Current position state in the grid"""
    symbol: str
    total_quantity: int = 0
    total_cost: Decimal = Decimal('0')
    average_price: Decimal = Decimal('0')
    unrealized_pnl: Decimal = Decimal('0')
    realized_pnl: Decimal = Decimal('0')
    
    def update_position(self, quantity: int, price: Decimal, side: str):
        """Update position after a fill"""
        if side == 'BUY':
            new_total_cost = self.total_cost + (Decimal(str(quantity)) * price)
            self.total_quantity += quantity
            if self.total_quantity > 0:
                self.average_price = new_total_cost / Decimal(str(self.total_quantity))
            self.total_cost = new_total_cost
        elif side == 'SELL':
            if self.total_quantity >= quantity:
                # Calculate realized PnL for the sold portion
                cost_per_share = self.average_price if self.average_price > 0 else Decimal('0')
                realized_for_this_trade = (price - cost_per_share) * Decimal(str(quantity))
                self.realized_pnl += realized_for_this_trade
                
                # Update position
                self.total_quantity -= quantity
                if self.total_quantity == 0:
                    self.total_cost = Decimal('0')
                    self.average_price = Decimal('0')
                else:
                    self.total_cost = self.average_price * Decimal(str(self.total_quantity))

@dataclass
class GridConfig:
    """Configuration for grid trading strategy"""
    # Basic Parameters
    symbol: str
    account_no: str
    loan_package_id: Optional[int] = None
    
    # Grid Structure
    grid_mode: str = "recursive"  # recursive, static, neat
    grid_levels: int = 10
    grid_spacing_pct: Decimal = Decimal('0.02')  # 2% spacing between levels
    grid_span_pct: Decimal = Decimal('0.20')  # 20% total grid span
    
    # Order Quantities
    initial_qty_pct: Decimal = Decimal('0.10')  # 10% of capital per initial order
    ddown_factor: Decimal = Decimal('1.5')  # Quantity multiplier for DCA
    max_position_size: int = 10000  # Maximum total position
    
    # Take Profit Settings
    min_markup_pct: Decimal = Decimal('0.005')  # 0.5% minimum markup
    markup_range_pct: Decimal = Decimal('0.015')  # 1.5% markup range
    
    # Risk Management
    wallet_exposure_limit_pct: Decimal = Decimal('0.30')  # 30% max exposure
    max_drawdown_pct: Decimal = Decimal('0.10')  # 10% max drawdown
    stop_loss_pct: Optional[Decimal] = None  # Optional stop loss
    
    # EMA Settings for smoothing
    ema_span_0: int = 12
    ema_span_1: int = 26
    use_ema_smoothing: bool = True
    
    # Operational
    price_precision: int = 0  # For VN stocks, typically 1 VND precision
    min_order_value: Decimal = Decimal('100000')  # 100k VND minimum order
    
    def validate(self) -> List[str]:
        """Validate configuration parameters"""
        errors = []
        
        if self.grid_levels < 2:
            errors.append("Grid levels must be at least 2")
        
        if self.grid_spacing_pct <= 0:
            errors.append("Grid spacing must be positive")
            
        if self.initial_qty_pct <= 0 or self.initial_qty_pct > 1:
            errors.append("Initial quantity percentage must be between 0 and 1")
            
        if self.wallet_exposure_limit_pct <= 0 or self.wallet_exposure_limit_pct > 1:
            errors.append("Wallet exposure limit must be between 0 and 1")
            
        if self.ddown_factor < 1:
            errors.append("DCA factor must be >= 1")
            
        return errors

class EMASmoother:
    """Exponential Moving Average calculator for smoothing entries"""
    
    def __init__(self, span_0: int = 12, span_1: int = 26):
        self.span_0 = span_0
        self.span_1 = span_1
        self.ema_0_values = []
        self.ema_1_values = []
        
    def add_price(self, price: Decimal) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """Add a new price and return updated EMAs"""
        self.ema_0_values.append(price)
        self.ema_1_values.append(price)
        
        # Keep only necessary values for calculation
        if len(self.ema_0_values) > self.span_0 * 2:
            self.ema_0_values = self.ema_0_values[-self.span_0:]
        if len(self.ema_1_values) > self.span_1 * 2:
            self.ema_1_values = self.ema_1_values[-self.span_1:]
            
        ema_0 = self._calculate_ema(self.ema_0_values, self.span_0)
        ema_1 = self._calculate_ema(self.ema_1_values, self.span_1)
        
        return ema_0, ema_1
    
    def _calculate_ema(self, values: List[Decimal], span: int) -> Optional[Decimal]:
        """Calculate EMA for given values and span"""
        if len(values) == 0:
            return None
            
        if len(values) == 1:
            return values[0]
            
        multiplier = Decimal('2') / (Decimal(str(span)) + Decimal('1'))
        ema = values[0]
        
        for value in values[1:]:
            ema = (value * multiplier) + (ema * (Decimal('1') - multiplier))
            
        return ema

class PriceUtils:
    """Utility functions for price calculations"""
    
    @staticmethod
    def round_price(price: Decimal, precision: int = 0) -> Decimal:
        """Round price to specified precision"""
        if precision == 0:
            return price.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        else:
            places = Decimal('0.1') ** precision
            return price.quantize(places, rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calculate_grid_prices(center_price: Decimal, grid_levels: int, 
                            spacing_pct: Decimal, mode: str = "symmetric") -> List[Decimal]:
        """Calculate grid price levels"""
        prices = []
        
        if mode == "symmetric":
            # Create symmetric grid around center price
            for i in range(-grid_levels//2, grid_levels//2 + 1):
                if i == 0:
                    continue  # Skip center price
                level_price = center_price * (Decimal('1') + (spacing_pct * Decimal(str(i))))
                prices.append(level_price)
        else:
            # Create grid below current price for buying
            for i in range(1, grid_levels + 1):
                level_price = center_price * (Decimal('1') - (spacing_pct * Decimal(str(i))))
                if level_price > 0:
                    prices.append(level_price)
                    
        return sorted(prices)
    
    @staticmethod
    def calculate_quantity_for_price(available_capital: Decimal, price: Decimal, 
                                   qty_pct: Decimal, min_order_value: Decimal) -> int:
        """Calculate order quantity based on available capital and percentage"""
        order_value = available_capital * qty_pct
        
        if order_value < min_order_value:
            return 0
            
        quantity = int(order_value / price)
        return max(0, quantity)

class RiskManager:
    """Risk management utilities"""
    
    def __init__(self, config: GridConfig):
        self.config = config
        
    def check_wallet_exposure(self, current_position_value: Decimal, 
                            total_wallet_value: Decimal) -> bool:
        """Check if position exposure is within limits"""
        if total_wallet_value <= 0:
            return False
            
        exposure_ratio = current_position_value / total_wallet_value
        return exposure_ratio <= self.config.wallet_exposure_limit_pct
    
    def check_max_position_size(self, current_quantity: int, additional_quantity: int) -> bool:
        """Check if adding quantity would exceed max position size"""
        return (current_quantity + additional_quantity) <= self.config.max_position_size
    
    def calculate_stop_loss_price(self, average_price: Decimal) -> Optional[Decimal]:
        """Calculate stop loss price if enabled"""
        if self.config.stop_loss_pct is None:
            return None
            
        return average_price * (Decimal('1') - self.config.stop_loss_pct)
    
    def should_stop_trading(self, current_pnl: Decimal, initial_capital: Decimal) -> bool:
        """Check if trading should be stopped due to drawdown"""
        if initial_capital <= 0:
            return True
            
        drawdown_ratio = abs(current_pnl) / initial_capital
        return drawdown_ratio >= self.config.max_drawdown_pct
