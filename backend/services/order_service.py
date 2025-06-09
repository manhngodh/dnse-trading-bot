from typing import Dict, Any, List
from dnse_client import DNSEClient
from core.data_structures import OrderRequest

class OrderService:
    def __init__(self):
        self.client = DNSEClient()
    
    def place_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Place a new order
        """
        order_request = OrderRequest(**order_data)
        return self.client.place_order(order_request)
    
    def get_order_details(self, order_id: str, account_no: str) -> Dict[str, Any]:
        """
        Get details of a specific order
        """
        return self.client.get_order_details(order_id, account_no)
    
    def cancel_order(self, order_id: str, account_no: str) -> Dict[str, Any]:
        """
        Cancel a pending order
        """
        return self.client.cancel_order(order_id, account_no)
    
    def get_pending_orders(self, account_no: str) -> List[Dict[str, Any]]:
        """
        Get all pending orders for an account
        """
        orders = self.client.get_orders(account_no)
        
        # Filter for pending orders only
        pending_statuses = ["pending", "pendingNew", "new", "partiallyFilled"]
        pending_orders = [order for order in orders if order.get("orderStatus") in pending_statuses]
        
        return pending_orders
        
    def get_orders(self, account_no: str) -> List[Dict[str, Any]]:
        """
        Get all orders for an account (includes orders with any status)
        
        Args:
            account_no: The account number
            
        Returns:
            List of all orders for the account
        """
        return self.client.get_orders(account_no)
