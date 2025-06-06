from typing import Dict, Any
from ..dnse_client import DNSEClient
from ..exceptions import DNSEAPIError

class PortfolioService:
    def __init__(self):
        self.dnse_client = DNSEClient()
        self.ui_client = None
        self.demo_client = None
        
        # Try importing UI client
        try:
            from ui_dnse_client import UIDNSEClient
            self.ui_client = UIDNSEClient()
        except ImportError:
            pass
            
        # Try importing demo client 
        try:
            from ..clients.demo_client import DemoTradingClient
            self.demo_client = DemoTradingClient()
        except ImportError:
            pass
    
    def get_portfolio(self, account_no: str) -> Dict[str, Any]:
        """Get portfolio information for a DNSE account"""
        return self.dnse_client.get_portfolio(account_no)
    
    def get_buying_power(self, account_no: str) -> Dict[str, Any]:
        """Get buying power information for a DNSE account"""
        return self.dnse_client.get_buying_power(account_no)

    def get_portfolio_ui(self, account_index: int) -> Dict[str, Any]:
        """Get portfolio using UI client"""
        if not self.ui_client:
            raise DNSEAPIError('DNSE UI client not available')
        return self.ui_client.get_portfolio(account_index)
        
    def get_demo_portfolio(self, account_no: str) -> Dict[str, Any]:
        """Get portfolio for demo account"""
        if not self.demo_client:
            raise DNSEAPIError('Demo client not available')
        if not self.demo_client.is_authenticated:
            raise DNSEAPIError('Must login to demo client first')
        return self.demo_client.get_portfolio(account_no)
        
    def reset_demo_portfolio(self, account_no: str) -> None:
        """Reset demo portfolio to initial state"""
        if not self.demo_client:
            raise DNSEAPIError('Demo client not available')
        if not self.demo_client.is_authenticated:
            raise DNSEAPIError('Must login to demo client first')
        self.demo_client.reset_portfolio(account_no)
