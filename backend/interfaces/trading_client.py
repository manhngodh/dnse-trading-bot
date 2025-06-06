from abc import ABC, abstractmethod
from typing import Dict, Any, List

class ITradingClient(ABC):
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the trading platform"""
        pass
    
    @abstractmethod
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get market data for a symbol"""
        pass
    
    @abstractmethod
    def place_order(self, order_request: Dict[str, Any]) -> Dict[str, Any]:
        """Place a trading order"""
        pass
    
    @abstractmethod
    def get_portfolio(self, account_no: str) -> Dict[str, Any]:
        """Get portfolio information"""
        pass
    
    @abstractmethod
    def get_pending_orders(self, account_no: str) -> List[Dict[str, Any]]:
        """Get pending orders"""
        pass
