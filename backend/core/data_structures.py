from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from enum import Enum

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(Enum):
    LIMIT = "LO"
    MARKET = "MP"
    ATO = "ATO"
    ATC = "ATC"

@dataclass
class MarketData:
    symbol: str
    price: float
    change: float = 0.0
    change_percent: float = 0.0
    volume: int = 0
    high: float = 0.0
    low: float = 0.0
    open: float = 0.0
    close: float = 0.0
    bid: float = 0.0
    ask: float = 0.0
    timestamp: Optional[datetime] = None
    
    def to_dict(self):
        return {
            'symbol': self.symbol,
            'price': self.price,
            'change': self.change,
            'change_percent': self.change_percent,
            'volume': self.volume,
            'high': self.high,
            'low': self.low,
            'open': self.open,
            'close': self.close,
            'bid': self.bid,
            'ask': self.ask,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

@dataclass
class OrderRequest:
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    price: float
    account_no: str
    loan_package_id: Optional[str] = None
