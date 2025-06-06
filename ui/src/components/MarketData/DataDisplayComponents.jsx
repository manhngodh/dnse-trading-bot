import React from 'react';

const PriceChange = ({ current, previous, className = '' }) => {
    const change = current - previous;
    const percentChange = (change / previous) * 100;
    const isPositive = change > 0;
    const isNegative = change < 0;
    
    const getChangeColor = () => {
        if (isPositive) return 'text-green-600';
        if (isNegative) return 'text-red-600';
        return 'text-gray-600';
    };
    
    const getChangeIcon = () => {
        if (isPositive) return '▲';
        if (isNegative) return '▼';
        return '■';
    };
    
    return (
        <span className={`${getChangeColor()} ${className}`}>
            {getChangeIcon()} {Math.abs(change).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ({Math.abs(percentChange).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}%)
        </span>
    );
};

// Component for displaying stock basic info
export const StockInfoCard = ({ data, loading }) => {
    if (loading) {
        return (
            <div className="bg-white rounded-lg shadow-md p-4 animate-pulse">
                <div className="h-6 bg-gray-200 rounded w-1/3 mb-2"></div>
                <div className="h-10 bg-gray-200 rounded w-1/2 mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-2/3"></div>
            </div>
        );
    }
    
    if (!data) {
        return (
            <div className="bg-white rounded-lg shadow-md p-4 text-gray-500">
                No data available
            </div>
        );
    }
    
    return (
        <div className="bg-white rounded-lg shadow-md p-4">
            <div className="flex justify-between items-center mb-2">
                <div>
                    <h3 className="text-lg font-semibold">{data.symbol}</h3>
                    <p className="text-sm text-gray-500">{data.fullName || 'N/A'}</p>
                </div>
                <div className="text-right">
                    <p className="text-xl font-bold">{parseFloat(data.matchPrice).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
                    {data.refPrice && (
                        <PriceChange 
                            current={parseFloat(data.matchPrice)} 
                            previous={parseFloat(data.refPrice)} 
                            className="text-sm"
                        />
                    )}
                </div>
            </div>
            
            <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                    <p className="text-gray-500">Open: <span className="text-gray-700">{parseFloat(data.openPrice || 0).toLocaleString()}</span></p>
                    <p className="text-gray-500">High: <span className="text-gray-700">{parseFloat(data.highPrice || 0).toLocaleString()}</span></p>
                </div>
                <div>
                    <p className="text-gray-500">Low: <span className="text-gray-700">{parseFloat(data.lowPrice || 0).toLocaleString()}</span></p>
                    <p className="text-gray-500">Volume: <span className="text-gray-700">{parseInt(data.matchQtty || 0).toLocaleString()}</span></p>
                </div>
            </div>
        </div>
    );
};

// Component for displaying top price (bid/ask) information
export const TopPriceTable = ({ data, loading }) => {
    if (loading) {
        return (
            <div className="bg-white rounded-lg shadow-md p-4 animate-pulse">
                <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
                <div className="space-y-2">
                    {[...Array(5)].map((_, i) => (
                        <div key={i} className="flex justify-between">
                            <div className="h-4 bg-gray-200 rounded w-1/3"></div>
                            <div className="h-4 bg-gray-200 rounded w-1/3"></div>
                        </div>
                    ))}
                </div>
            </div>
        );
    }
    
    if (!data || !data.bidOfferList || data.bidOfferList.length === 0) {
        return (
            <div className="bg-white rounded-lg shadow-md p-4 text-gray-500">
                No order book data available
            </div>
        );
    }
    
    return (
        <div className="bg-white rounded-lg shadow-md p-4">
            <h3 className="text-lg font-semibold mb-2">Order Book - {data.symbol}</h3>
            
            <div className="grid grid-cols-4 gap-2 font-semibold text-sm mb-1 border-b pb-1">
                <div>Bid Vol</div>
                <div>Bid</div>
                <div>Ask</div>
                <div>Ask Vol</div>
            </div>
            
            {data.bidOfferList.map((level, index) => (
                <div key={index} className="grid grid-cols-4 gap-2 text-sm py-1">
                    <div className="text-green-600">
                        {parseInt(level.bidQtty || 0).toLocaleString()}
                    </div>
                    <div className="text-green-600">
                        {parseFloat(level.bidPrice || 0).toLocaleString()}
                    </div>
                    <div className="text-red-600">
                        {parseFloat(level.offerPrice || 0).toLocaleString()}
                    </div>
                    <div className="text-red-600">
                        {parseInt(level.offerQtty || 0).toLocaleString()}
                    </div>
                </div>
            ))}
        </div>
    );
};

// Component for displaying recent trades (ticks)
export const TicksTable = ({ ticks, loading, limit = 10 }) => {
    if (loading) {
        return (
            <div className="bg-white rounded-lg shadow-md p-4 animate-pulse">
                <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
                <div className="space-y-2">
                    {[...Array(5)].map((_, i) => (
                        <div key={i} className="flex justify-between">
                            <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                            <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                            <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                        </div>
                    ))}
                </div>
            </div>
        );
    }
    
    if (!ticks || ticks.length === 0) {
        return (
            <div className="bg-white rounded-lg shadow-md p-4 text-gray-500">
                No recent trades available
            </div>
        );
    }
    
    const limitedTicks = ticks.slice(0, limit);
    
    return (
        <div className="bg-white rounded-lg shadow-md p-4">
            <h3 className="text-lg font-semibold mb-2">Recent Trades - {limitedTicks[0].symbol}</h3>
            
            <div className="grid grid-cols-4 gap-2 font-semibold text-sm mb-1 border-b pb-1">
                <div>Time</div>
                <div>Price</div>
                <div>Quantity</div>
                <div>Side</div>
            </div>
            
            {limitedTicks.map((tick, index) => {
                const time = new Date(tick.sendingTime);
                const timeString = time.toLocaleTimeString();
                const side = tick.side;
                const sideColor = side === 'B' ? 'text-green-600' : side === 'S' ? 'text-red-600' : 'text-gray-600';
                
                return (
                    <div key={index} className="grid grid-cols-4 gap-2 text-sm py-1">
                        <div>{timeString}</div>
                        <div className={sideColor}>
                            {parseFloat(tick.matchPrice || 0).toLocaleString()}
                        </div>
                        <div>
                            {parseInt(tick.matchQtty || 0).toLocaleString()}
                        </div>
                        <div className={sideColor}>
                            {side === 'B' ? 'Buy' : side === 'S' ? 'Sell' : side}
                        </div>
                    </div>
                );
            })}
        </div>
    );
};

// Component for displaying market indices
export const MarketIndexCard = ({ data, loading }) => {
    if (loading) {
        return (
            <div className="bg-white rounded-lg shadow-md p-4 animate-pulse">
                <div className="h-6 bg-gray-200 rounded w-1/3 mb-2"></div>
                <div className="h-10 bg-gray-200 rounded w-1/2"></div>
            </div>
        );
    }
    
    if (!data) {
        return (
            <div className="bg-white rounded-lg shadow-md p-4 text-gray-500">
                No index data available
            </div>
        );
    }
    
    return (
        <div className="bg-white rounded-lg shadow-md p-4">
            <h3 className="text-lg font-semibold">{data.indexName || 'Index'}</h3>
            
            <div className="flex items-center mt-2">
                <p className="text-2xl font-bold mr-2">
                    {parseFloat(data.indexValue).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
                {data.refIndex && (
                    <PriceChange 
                        current={parseFloat(data.indexValue)} 
                        previous={parseFloat(data.refIndex)} 
                    />
                )}
            </div>
            
            <div className="mt-2 text-sm">
                <p className="text-gray-500">
                    Volume: <span className="text-gray-700">{parseInt(data.totalQtty || 0).toLocaleString()}</span>
                </p>
                <p className="text-gray-500">
                    Value: <span className="text-gray-700">{(parseFloat(data.totalValue || 0) / 1000000).toLocaleString()} M</span>
                </p>
            </div>
        </div>
    );
};

// Component for displaying board events
export const BoardEventCard = ({ data, loading }) => {
    if (loading) {
        return (
            <div className="bg-white rounded-lg shadow-md p-4 animate-pulse">
                <div className="h-6 bg-gray-200 rounded w-1/3 mb-2"></div>
                <div className="h-5 bg-gray-200 rounded w-1/2"></div>
            </div>
        );
    }
    
    if (!data) {
        return (
            <div className="bg-white rounded-lg shadow-md p-4 text-gray-500">
                No board event data available
            </div>
        );
    }
    
    const getSessionName = (sessionId) => {
        const sessions = {
            'PREOPEN': 'Pre-Open',
            'OPEN': 'Open',
            'CLOSE': 'Close',
            'ATC': 'At The Close',
            'BREAK': 'Break',
            'PRECLOSE': 'Pre-Close',
            'POSTCLOSE': 'Post-Close'
        };
        
        return sessions[sessionId] || sessionId;
    };
    
    const getSessionColor = (sessionId) => {
        if (sessionId === 'OPEN') return 'bg-green-100 text-green-800';
        if (sessionId === 'CLOSE') return 'bg-red-100 text-red-800';
        return 'bg-blue-100 text-blue-800';
    };
    
    return (
        <div className="bg-white rounded-lg shadow-md p-4">
            <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold">Market Status</h3>
                <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${getSessionColor(data.sessionId)}`}
                >
                    {getSessionName(data.sessionId)}
                </span>
            </div>
            
            <div className="mt-2 text-sm">
                <p className="text-gray-500">
                    Market: <span className="text-gray-700">{data.market || 'N/A'}</span>
                </p>
                <p className="text-gray-500">
                    Product: <span className="text-gray-700">{data.tsczProductGrpId || 'N/A'}</span>
                </p>
                <p className="text-gray-500">
                    Time: <span className="text-gray-700">
                        {new Date(data.sendingTime).toLocaleString()}
                    </span>
                </p>
            </div>
        </div>
    );
};
