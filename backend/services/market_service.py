from typing import Dict, Any
from ..dnse_client import DNSEClient

class MarketService:
    def __init__(self):
        self.client = DNSEClient()
    
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get stock information including price limits and lot size
        """
        return self.client.get_stock_info(symbol)
    
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get real-time market data for a symbol
        """
        market_data = self.client.get_market_data(symbol)
        return market_data.to_dict()
