import React from 'react';
import { X } from 'lucide-react';

const PendingOrders = ({ orders, onCancelOrder }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4">Pending Orders</h3>
      
      {orders.length === 0 ? (
        <p className="text-gray-500 text-center py-4">No pending orders</p>
      ) : (
        <div className="space-y-2">
          {orders.map((order, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <span className="font-medium">{order.symbol}</span>
                  <span className={`px-2 py-1 text-xs rounded ${
                    order.side === 'buy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {order.side?.toUpperCase()}
                  </span>
                </div>
                <div className="text-sm text-gray-600">
                  {order.quantity} @ {order.price?.toLocaleString()} VND
                </div>
              </div>
              
              <button
                onClick={() => onCancelOrder(order.orderId)}
                className="text-red-600 hover:text-red-800"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PendingOrders;
