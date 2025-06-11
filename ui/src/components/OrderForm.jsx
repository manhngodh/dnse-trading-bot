import React from 'react';
import { Send } from 'lucide-react';

const OrderForm = ({ formData, onChange, onSubmit, loading }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
        <Send className="h-5 w-5" />
        <span>Place Order</span>
      </h3>
      
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Symbol</label>
            <input
              type="text"
              value={formData.symbol}
              onChange={(e) => onChange({ ...formData, symbol: e.target.value.toUpperCase() })}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="VCI"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Side</label>
            <select
              value={formData.side}
              onChange={(e) => onChange({ ...formData, side: e.target.value })}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="buy">Buy</option>
              <option value="sell">Sell</option>
            </select>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Quantity</label>
            <input
              type="number"
              value={formData.quantity}
              onChange={(e) => onChange({ ...formData, quantity: e.target.value })}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="100"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Price</label>
            <input
              type="number"
              value={formData.price}
              onChange={(e) => onChange({ ...formData, price: e.target.value })}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="25000"
            />
          </div>
        </div>
        
        <button
          onClick={onSubmit}
          disabled={loading}
          className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 ${
            formData.side === 'buy' 
              ? 'bg-green-600 hover:bg-green-700 focus:ring-green-500' 
              : 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
          }`}
        >
          {loading ? 'Placing...' : `Place ${formData.side === 'buy' ? 'Buy' : 'Sell'} Order`}
        </button>
      </div>
    </div>
  );
};

export default OrderForm;
