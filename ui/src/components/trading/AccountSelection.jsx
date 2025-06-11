import React from 'react';

const AccountSelection = ({ accounts, selectedAccount, onAccountChange }) => {
  if (!accounts || accounts.length === 0) return null;

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4">Account Selection</h3>
      <select
        value={selectedAccount?.accountNo || ''}
        onChange={(e) => {
          const account = accounts.find(acc => acc.accountNo === e.target.value);
          onAccountChange(account);
        }}
        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
      >
        {accounts.map(account => (
          <option key={account.accountNo} value={account.accountNo}>
            {account.accountNo} - {account.accountType || 'Trading Account'}
          </option>
        ))}
      </select>
    </div>
  );
};

export default AccountSelection;
