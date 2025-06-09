// OrderService.js - API client for order-related endpoints

export default class OrderService {
  static async getPendingOrders(accountNo) {
    try {
      const response = await fetch(
        `/api/orders/pending?accountNo=${encodeURIComponent(accountNo)}`
      );
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to fetch pending orders");
      }
      return await response.json();
    } catch (error) {
      console.error("Error fetching pending orders:", error);
      throw error;
    }
  }

  static async getOrderDetails(orderId, accountNo) {
    try {
      const response = await fetch(
        `/api/orders/${encodeURIComponent(
          orderId
        )}?accountNo=${encodeURIComponent(accountNo)}`
      );
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to fetch order details");
      }
      return await response.json();
    } catch (error) {
      console.error("Error fetching order details:", error);
      throw error;
    }
  }

  static async cancelOrder(orderId, accountNo) {
    try {
      const response = await fetch(
        `/api/orders/${encodeURIComponent(
          orderId
        )}?accountNo=${encodeURIComponent(accountNo)}`,
        {
          method: "DELETE",
        }
      );
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to cancel order");
      }
      return await response.json();
    } catch (error) {
      console.error("Error canceling order:", error);
      throw error;
    }
  }

  static async placeOrder(orderData) {
    try {
      const response = await fetch("/api/orders", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(orderData),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to place order");
      }
      return await response.json();
    } catch (error) {
      console.error("Error placing order:", error);
      throw error;
    }
  }

  static async getOrderHistory(accountNo, filters = {}) {
    // Since there's no specific history API in DNSE, we'll use the regular orders endpoint
    // and filter on the client side
    const queryParams = new URLSearchParams();
    queryParams.append("accountNo", accountNo);

    // Add filters for backend filtering (status, symbol)
    if (filters.symbol) queryParams.append("symbol", filters.symbol);
    if (filters.status) queryParams.append("status", filters.status);

    try {
      // Use the orders/history endpoint which will use the main orders endpoint internally
      const response = await fetch(
        `/api/orders/history?${queryParams.toString()}`
      );
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to fetch order history");
      }

      const orders = await response.json();

      // Additional client-side filtering for date range if needed
      let filteredOrders = orders;

      if (filters.startDate || filters.endDate) {
        filteredOrders = orders.filter((order) => {
          const orderDate = new Date(order.createdDate || order.transDate);

          if (filters.startDate) {
            const startDate = new Date(filters.startDate);
            if (orderDate < startDate) return false;
          }

          if (filters.endDate) {
            const endDate = new Date(filters.endDate);
            // Add a day to include the end date fully
            endDate.setDate(endDate.getDate() + 1);
            if (orderDate > endDate) return false;
          }

          return true;
        });
      }

      return filteredOrders;
    } catch (error) {
      console.error("Error fetching order history:", error);
      throw error;
    }
  }
}
