import React from 'react';
import { DollarSign } from 'lucide-react';

const BuyingPower = ({ buyingPower }) => {
  if (!buyingPower) return null;

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
        <DollarSign className="h-5 w-5" />
        <span>Buying Power</span>
      </h3>
      <div className="text-2xl font-bold text-green-600">
        {buyingPower.buyingPower?.toLocaleString()} VND
      </div>
      <p className="text-sm text-gray-600 mt-1">Available for trading</p>
    </div>
  );
};

export default BuyingPower;
