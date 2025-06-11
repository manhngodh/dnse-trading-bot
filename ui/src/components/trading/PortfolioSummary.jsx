import React from 'react';
import { Activity } from 'lucide-react';

const PortfolioSummary = ({ portfolio }) => {
  if (!portfolio) return null;

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
        <Activity className="h-5 w-5" />
        <span>Portfolio Summary</span>
      </h3>
      <div className="space-y-2">
        <div className="flex justify-between">
          <span className="text-gray-600">Total Value:</span>
          <span className="font-semibold">{portfolio.totalValue?.toLocaleString()} VND</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">Cash:</span>
          <span className="font-semibold">{portfolio.cash?.toLocaleString()} VND</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">Securities:</span>
          <span className="font-semibold">{portfolio.securitiesValue?.toLocaleString()} VND</span>
        </div>
      </div>
    </div>
  );
};

export default PortfolioSummary;
