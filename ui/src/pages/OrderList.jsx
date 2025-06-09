// OrderList.jsx - Page for displaying and managing orders

import React, { useState, useEffect } from 'react';
import { 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Search, 
  RefreshCw, 
  Calendar, 
  X, 
  Eye, 
  Filter 
} from 'lucide-react';
import OrderService from '../services/OrderService';

const OrderList = ({ authData }) => {
  // State management
  const [activeTab, setActiveTab] = useState('pending'); // 'pending' or 'history'
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [showOrderDetails, setShowOrderDetails] = useState(false);
  
  // Filter state
  const [filters, setFilters] = useState({
    symbol: '',
    startDate: '',
    endDate: '',
    status: '',
  });

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const ordersPerPage = 10;

  // Get current account from authData
  const currentAccount = authData?.accounts?.length > 0 ? authData.accounts[0] : null;
  const accountNo = currentAccount?.accountNo;

  // Fetch orders on component mount and when dependencies change
  useEffect(() => {
    if (accountNo) {
      fetchOrders();
    }
  }, [accountNo, activeTab, currentPage]);

  const fetchOrders = async () => {
    if (!accountNo) return;
    
    setLoading(true);
    setError(null);
    
    try {
      let fetchedOrders;
      
      if (activeTab === 'pending') {
        fetchedOrders = await OrderService.getPendingOrders(accountNo);
      } else {
        // Apply filters for history
        fetchedOrders = await OrderService.getOrderHistory(accountNo, {
          symbol: filters.symbol || undefined,
          startDate: filters.startDate || undefined,
          endDate: filters.endDate || undefined,
          status: filters.status || undefined,
        });
      }
      
      setOrders(fetchedOrders);
    } catch (err) {
      setError(err.message || 'Failed to fetch orders');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (order) => {
    setLoading(true);
    setError(null);
    
    try {
      const orderDetails = await OrderService.getOrderDetails(order.orderId, accountNo);
      setSelectedOrder(orderDetails);
      setShowOrderDetails(true);
    } catch (err) {
      setError(err.message || 'Failed to fetch order details');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelOrder = async (orderId) => {
    if (!window.confirm('Are you sure you want to cancel this order?')) {
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      await OrderService.cancelOrder(orderId, accountNo);
      setSuccess('Order cancelled successfully');
      fetchOrders(); // Refresh orders after cancellation
    } catch (err) {
      setError(err.message || 'Failed to cancel order');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const applyFilters = () => {
    setCurrentPage(1);
    fetchOrders();
  };

  const resetFilters = () => {
    setFilters({
      symbol: '',
      startDate: '',
      endDate: '',
      status: '',
    });
    setCurrentPage(1);
    fetchOrders();
  };

  // Handle pagination
  const paginate = (pageNumber) => setCurrentPage(pageNumber);
  
  const formatDateTime = (timestamp) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp).toLocaleString();
  };
  
  const formatCurrency = (amount) => {
    if (amount === undefined || amount === null) return 'N/A';
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
  };
  
  const getOrderStatusClass = (status) => {
    switch (status?.toLowerCase()) {
      case 'filled':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
      case 'rejected':
        return 'bg-red-100 text-red-800';
      case 'pending':
      case 'new':
        return 'bg-yellow-100 text-yellow-800';
      case 'partially_filled':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Orders</h1>
      
      {!accountNo && (
        <div className="bg-yellow-100 text-yellow-800 p-4 rounded-md mb-6">
          Please connect your DNSE account to view orders.
        </div>
      )}
      
      {error && (
        <div className="bg-red-100 text-red-800 p-4 rounded-md mb-6 flex justify-between items-center">
          <div className="flex items-center">
            <AlertCircle className="mr-2 h-5 w-5" />
            {error}
          </div>
          <button onClick={() => setError(null)}>
            <X className="h-5 w-5" />
          </button>
        </div>
      )}
      
      {success && (
        <div className="bg-green-100 text-green-800 p-4 rounded-md mb-6 flex justify-between items-center">
          <div className="flex items-center">
            <CheckCircle className="mr-2 h-5 w-5" />
            {success}
          </div>
          <button onClick={() => setSuccess(null)}>
            <X className="h-5 w-5" />
          </button>
        </div>
      )}
      
      {accountNo && (
        <>
          {/* Tabs */}
          <div className="border-b border-gray-200 mb-6">
            <nav className="flex -mb-px space-x-8" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('pending')}
                className={`py-3 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'pending'
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Pending Orders
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`py-3 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'history'
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Order History
              </button>
            </nav>
          </div>
          
          {/* Filters (visible only in history tab) */}
          {activeTab === 'history' && (
            <div className="bg-gray-50 p-4 rounded-md mb-6">
              <div className="flex items-center mb-2">
                <Filter className="h-5 w-5 mr-2 text-gray-500" />
                <h3 className="font-medium text-gray-700">Filters</h3>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Symbol
                  </label>
                  <div className="relative rounded-md shadow-sm">
                    <input
                      type="text"
                      name="symbol"
                      value={filters.symbol}
                      onChange={handleFilterChange}
                      className="focus:ring-primary focus:border-primary block w-full pl-3 pr-10 py-2 sm:text-sm border-gray-300 rounded-md"
                      placeholder="e.g. VIC"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    From Date
                  </label>
                  <div className="relative rounded-md shadow-sm">
                    <input
                      type="date"
                      name="startDate"
                      value={filters.startDate}
                      onChange={handleFilterChange}
                      className="focus:ring-primary focus:border-primary block w-full pl-3 pr-10 py-2 sm:text-sm border-gray-300 rounded-md"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    To Date
                  </label>
                  <div className="relative rounded-md shadow-sm">
                    <input
                      type="date"
                      name="endDate"
                      value={filters.endDate}
                      onChange={handleFilterChange}
                      className="focus:ring-primary focus:border-primary block w-full pl-3 pr-10 py-2 sm:text-sm border-gray-300 rounded-md"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Status
                  </label>
                  <select
                    name="status"
                    value={filters.status}
                    onChange={handleFilterChange}
                    className="focus:ring-primary focus:border-primary block w-full pl-3 pr-10 py-2 sm:text-sm border-gray-300 rounded-md"
                  >
                    <option value="">All Statuses</option>
                    <option value="filled">Filled</option>
                    <option value="cancelled">Cancelled</option>
                    <option value="rejected">Rejected</option>
                    <option value="partially_filled">Partially Filled</option>
                  </select>
                </div>
              </div>
              
              <div className="flex justify-end mt-4 space-x-3">
                <button
                  type="button"
                  onClick={resetFilters}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50"
                >
                  Reset
                </button>
                <button
                  type="button"
                  onClick={applyFilters}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary hover:bg-primary-dark"
                >
                  Apply Filters
                </button>
              </div>
            </div>
          )}
          
          {/* Refresh button */}
          <div className="flex justify-end mb-4">
            <button
              onClick={fetchOrders}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary hover:bg-primary-dark"
              disabled={loading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
          
          {/* Orders table */}
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Symbol
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Side
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Quantity
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Price
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created At
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan="8" className="px-6 py-4 text-center">
                      <div className="flex justify-center">
                        <RefreshCw className="h-6 w-6 text-primary animate-spin" />
                      </div>
                      <p className="text-gray-500 mt-2">Loading orders...</p>
                    </td>
                  </tr>
                ) : orders.length === 0 ? (
                  <tr>
                    <td colSpan="8" className="px-6 py-4 text-center text-gray-500">
                      No orders found
                    </td>
                  </tr>
                ) : (
                  orders.map((order) => (
                    <tr key={order.orderId} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {order.symbol}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {order.orderType || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={order.side === 'buy' ? 'text-green-600' : 'text-red-600'}>
                          {order.side?.toUpperCase() || 'N/A'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {order.quantity || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatCurrency(order.price)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getOrderStatusClass(order.status)}`}>
                          {order.status || 'Unknown'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDateTime(order.createdAt)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleViewDetails(order)}
                            className="text-primary hover:text-primary-dark"
                            title="View details"
                          >
                            <Eye className="h-5 w-5" />
                          </button>
                          
                          {activeTab === 'pending' && (
                            <button
                              onClick={() => handleCancelOrder(order.orderId)}
                              className="text-red-600 hover:text-red-900"
                              title="Cancel order"
                              disabled={loading}
                            >
                              <X className="h-5 w-5" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          
          {/* Pagination */}
          {orders.length > 0 && (
            <div className="flex items-center justify-between mt-6">
              <div className="text-sm text-gray-500">
                Showing {orders.length} results
              </div>
              <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                {Array.from({ length: Math.ceil(orders.length / ordersPerPage) }).map((_, index) => (
                  <button
                    key={index}
                    onClick={() => paginate(index + 1)}
                    className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                      currentPage === index + 1
                        ? 'z-10 bg-primary text-white border-primary'
                        : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                    }`}
                  >
                    {index + 1}
                  </button>
                ))}
              </nav>
            </div>
          )}
        </>
      )}
      
      {/* Order Details Modal */}
      {showOrderDetails && selectedOrder && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center px-6 py-4 border-b">
              <h3 className="text-lg font-medium text-gray-900">
                Order Details
              </h3>
              <button onClick={() => setShowOrderDetails(false)} className="text-gray-400 hover:text-gray-500">
                <X className="h-5 w-5" />
              </button>
            </div>
            
            <div className="px-6 py-4">
              <dl className="grid grid-cols-2 gap-x-4 gap-y-6">
                <div className="col-span-1">
                  <dt className="text-sm font-medium text-gray-500">Order ID</dt>
                  <dd className="mt-1 text-sm text-gray-900">{selectedOrder.orderId}</dd>
                </div>
                
                <div className="col-span-1">
                  <dt className="text-sm font-medium text-gray-500">Symbol</dt>
                  <dd className="mt-1 text-sm text-gray-900">{selectedOrder.symbol}</dd>
                </div>
                
                <div className="col-span-1">
                  <dt className="text-sm font-medium text-gray-500">Side</dt>
                  <dd className={`mt-1 text-sm ${selectedOrder.side === 'buy' ? 'text-green-600' : 'text-red-600'}`}>
                    {selectedOrder.side?.toUpperCase()}
                  </dd>
                </div>
                
                <div className="col-span-1">
                  <dt className="text-sm font-medium text-gray-500">Order Type</dt>
                  <dd className="mt-1 text-sm text-gray-900">{selectedOrder.orderType}</dd>
                </div>
                
                <div className="col-span-1">
                  <dt className="text-sm font-medium text-gray-500">Quantity</dt>
                  <dd className="mt-1 text-sm text-gray-900">{selectedOrder.quantity}</dd>
                </div>
                
                <div className="col-span-1">
                  <dt className="text-sm font-medium text-gray-500">Price</dt>
                  <dd className="mt-1 text-sm text-gray-900">{formatCurrency(selectedOrder.price)}</dd>
                </div>
                
                <div className="col-span-1">
                  <dt className="text-sm font-medium text-gray-500">Status</dt>
                  <dd className="mt-1">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getOrderStatusClass(selectedOrder.status)}`}>
                      {selectedOrder.status}
                    </span>
                  </dd>
                </div>
                
                <div className="col-span-1">
                  <dt className="text-sm font-medium text-gray-500">Filled Quantity</dt>
                  <dd className="mt-1 text-sm text-gray-900">{selectedOrder.filledQuantity || '0'}</dd>
                </div>
                
                <div className="col-span-1">
                  <dt className="text-sm font-medium text-gray-500">Created At</dt>
                  <dd className="mt-1 text-sm text-gray-900">{formatDateTime(selectedOrder.createdAt)}</dd>
                </div>
                
                <div className="col-span-1">
                  <dt className="text-sm font-medium text-gray-500">Updated At</dt>
                  <dd className="mt-1 text-sm text-gray-900">{formatDateTime(selectedOrder.updatedAt)}</dd>
                </div>
                
                {selectedOrder.cancelReason && (
                  <div className="col-span-2">
                    <dt className="text-sm font-medium text-gray-500">Cancel Reason</dt>
                    <dd className="mt-1 text-sm text-red-600">{selectedOrder.cancelReason}</dd>
                  </div>
                )}
                
                {selectedOrder.rejectReason && (
                  <div className="col-span-2">
                    <dt className="text-sm font-medium text-gray-500">Reject Reason</dt>
                    <dd className="mt-1 text-sm text-red-600">{selectedOrder.rejectReason}</dd>
                  </div>
                )}
              </dl>
            </div>
            
            <div className="px-6 py-4 border-t flex justify-end">
              {activeTab === 'pending' && selectedOrder.status?.toLowerCase() === 'pending' && (
                <button
                  onClick={() => {
                    handleCancelOrder(selectedOrder.orderId);
                    setShowOrderDetails(false);
                  }}
                  className="ml-3 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700"
                >
                  Cancel Order
                </button>
              )}
              <button
                onClick={() => setShowOrderDetails(false)}
                className="ml-3 inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OrderList;
