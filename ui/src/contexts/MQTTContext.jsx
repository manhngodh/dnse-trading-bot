import React, { createContext, useContext, useEffect, useState } from 'react';
import mqttService from '../services/MQTTService';

// Create context
const MQTTContext = createContext(null);

export const MQTTProvider = ({ children, investorId, token }) => {
    const [connectionStatus, setConnectionStatus] = useState({
        connected: false,
        error: null
    });
    
    const [marketData, setMarketData] = useState({
        stockInfo: {}, // { symbolKey: data }
        topPrice: {}, 
        ticks: {},
        indices: {}, // { indexName: data }
        ohlc: {},    // { symbol_resolution: data }
        boardEvents: {} // { market_product: data }
    });

    // Active subscriptions tracker
    const [activeSubscriptions, setActiveSubscriptions] = useState([]);

    useEffect(() => {
        // Connect to MQTT broker when investorId and token are provided
        if (investorId && token) {
            connectMQTT();
        } else {
            mqttService.disconnect();
            setConnectionStatus({ connected: false, error: null });
        }

        // Add connection status listener
        const unsubscribeConnection = mqttService.onConnectionChange((connected, error) => {
            setConnectionStatus({ connected, error });
        });

        // Cleanup on unmount
        return () => {
            unsubscribeConnection();
            mqttService.disconnect();
        };
    }, [investorId, token]);

    // Connect to MQTT broker
    const connectMQTT = async () => {
        try {
            await mqttService.connect(investorId, token);
            setConnectionStatus({ connected: true, error: null });
        } catch (error) {
            console.error('Failed to connect to MQTT broker:', error);
            setConnectionStatus({ 
                connected: false, 
                error: error.message || 'Failed to connect to MQTT broker'
            });
        }
    };

    // Subscribe to stock info updates
    const subscribeToStockInfo = (symbol, callback) => {
        if (!connectionStatus.connected) {
            return false;
        }

        const topic = mqttService.buildTopics.stockInfo(symbol);
        
        // Register our internal handler
        const internalHandler = (data) => {
            setMarketData(prev => ({
                ...prev,
                stockInfo: {
                    ...prev.stockInfo,
                    [symbol]: data
                }
            }));
            
            // Call the user's callback if provided
            if (callback) callback(data);
        };
        
        const success = mqttService.subscribe(topic, internalHandler);
        
        if (success) {
            setActiveSubscriptions(prev => [...prev, { type: 'stockInfo', topic, symbol }]);
        }
        
        return success;
    };

    // Subscribe to top price updates
    const subscribeToTopPrice = (symbol, callback) => {
        if (!connectionStatus.connected) {
            return false;
        }

        const topic = mqttService.buildTopics.topPrice(symbol);
        
        // Register our internal handler
        const internalHandler = (data) => {
            setMarketData(prev => ({
                ...prev,
                topPrice: {
                    ...prev.topPrice,
                    [symbol]: data
                }
            }));
            
            // Call the user's callback if provided
            if (callback) callback(data);
        };
        
        const success = mqttService.subscribe(topic, internalHandler);
        
        if (success) {
            setActiveSubscriptions(prev => [...prev, { type: 'topPrice', topic, symbol }]);
        }
        
        return success;
    };

    // Subscribe to tick data
    const subscribeToTicks = (symbol, callback) => {
        if (!connectionStatus.connected) {
            return false;
        }

        const topic = mqttService.buildTopics.tick(symbol);
        
        // Register our internal handler
        const internalHandler = (data) => {
            setMarketData(prev => {
                // Add new tick to the beginning of the array (or create new array)
                const currentTicks = prev.ticks[symbol] || [];
                const newTicks = [data, ...currentTicks].slice(0, 100); // Keep last 100 ticks
                
                return {
                    ...prev,
                    ticks: {
                        ...prev.ticks,
                        [symbol]: newTicks
                    }
                };
            });
            
            // Call the user's callback if provided
            if (callback) callback(data);
        };
        
        const success = mqttService.subscribe(topic, internalHandler);
        
        if (success) {
            setActiveSubscriptions(prev => [...prev, { type: 'tick', topic, symbol }]);
        }
        
        return success;
    };

    // Subscribe to market index data
    const subscribeToIndex = (indexName, callback) => {
        if (!connectionStatus.connected) {
            return false;
        }

        const topic = mqttService.buildTopics.marketIndex(indexName);
        
        // Register our internal handler
        const internalHandler = (data) => {
            setMarketData(prev => ({
                ...prev,
                indices: {
                    ...prev.indices,
                    [indexName]: data
                }
            }));
            
            // Call the user's callback if provided
            if (callback) callback(data);
        };
        
        const success = mqttService.subscribe(topic, internalHandler);
        
        if (success) {
            setActiveSubscriptions(prev => [...prev, { type: 'index', topic, indexName }]);
        }
        
        return success;
    };

    // Subscribe to OHLC data
    const subscribeToOHLC = (type, resolution, symbol, callback) => {
        if (!connectionStatus.connected || !['stock', 'derivative', 'index'].includes(type)) {
            return false;
        }

        let topic;
        let key;
        
        if (type === 'stock') {
            topic = mqttService.buildTopics.stockOHLC(resolution, symbol);
            key = `stock_${symbol}_${resolution}`;
        } else if (type === 'derivative') {
            topic = mqttService.buildTopics.derivativeOHLC(resolution, symbol);
            key = `derivative_${symbol}_${resolution}`;
        } else if (type === 'index') {
            topic = mqttService.buildTopics.indexOHLC(resolution, symbol);
            key = `index_${symbol}_${resolution}`;
        }

        // Register our internal handler
        const internalHandler = (data) => {
            setMarketData(prev => ({
                ...prev,
                ohlc: {
                    ...prev.ohlc,
                    [key]: data
                }
            }));
            
            // Call the user's callback if provided
            if (callback) callback(data);
        };
        
        const success = mqttService.subscribe(topic, internalHandler);
        
        if (success) {
            setActiveSubscriptions(prev => [...prev, { 
                type: 'ohlc', 
                ohlcType: type,
                resolution,
                symbol, 
                topic,
                key
            }]);
        }
        
        return success;
    };

    // Subscribe to board events
    const subscribeToBoardEvent = (market, productGrpId, callback) => {
        if (!connectionStatus.connected) {
            return false;
        }

        const topic = mqttService.buildTopics.boardEvent(market, productGrpId);
        const key = `${market}_${productGrpId}`;
        
        // Register our internal handler
        const internalHandler = (data) => {
            setMarketData(prev => ({
                ...prev,
                boardEvents: {
                    ...prev.boardEvents,
                    [key]: data
                }
            }));
            
            // Call the user's callback if provided
            if (callback) callback(data);
        };
        
        const success = mqttService.subscribe(topic, internalHandler);
        
        if (success) {
            setActiveSubscriptions(prev => [...prev, { 
                type: 'boardEvent', 
                market, 
                productGrpId,
                topic, 
                key
            }]);
        }
        
        return success;
    };

    // Unsubscribe from a specific topic
    const unsubscribe = (type, params) => {
        let topic = '';
        let subscriptionIndex = -1;
        
        switch (type) {
            case 'stockInfo':
                topic = mqttService.buildTopics.stockInfo(params.symbol);
                subscriptionIndex = activeSubscriptions.findIndex(
                    sub => sub.type === 'stockInfo' && sub.symbol === params.symbol
                );
                break;
                
            case 'topPrice':
                topic = mqttService.buildTopics.topPrice(params.symbol);
                subscriptionIndex = activeSubscriptions.findIndex(
                    sub => sub.type === 'topPrice' && sub.symbol === params.symbol
                );
                break;
                
            case 'tick':
                topic = mqttService.buildTopics.tick(params.symbol);
                subscriptionIndex = activeSubscriptions.findIndex(
                    sub => sub.type === 'tick' && sub.symbol === params.symbol
                );
                break;
                
            case 'index':
                topic = mqttService.buildTopics.marketIndex(params.indexName);
                subscriptionIndex = activeSubscriptions.findIndex(
                    sub => sub.type === 'index' && sub.indexName === params.indexName
                );
                break;
                
            case 'ohlc':
                const { ohlcType, resolution, symbol } = params;
                if (ohlcType === 'stock') {
                    topic = mqttService.buildTopics.stockOHLC(resolution, symbol);
                } else if (ohlcType === 'derivative') {
                    topic = mqttService.buildTopics.derivativeOHLC(resolution, symbol);
                } else if (ohlcType === 'index') {
                    topic = mqttService.buildTopics.indexOHLC(resolution, symbol);
                }
                subscriptionIndex = activeSubscriptions.findIndex(
                    sub => sub.type === 'ohlc' && 
                           sub.ohlcType === ohlcType && 
                           sub.resolution === resolution && 
                           sub.symbol === symbol
                );
                break;
                
            case 'boardEvent':
                const { market, productGrpId } = params;
                topic = mqttService.buildTopics.boardEvent(market, productGrpId);
                subscriptionIndex = activeSubscriptions.findIndex(
                    sub => sub.type === 'boardEvent' && 
                           sub.market === market && 
                           sub.productGrpId === productGrpId
                );
                break;
                
            default:
                return false;
        }
        
        // Unsubscribe from MQTT
        mqttService.unsubscribe(topic);
        
        // Remove from active subscriptions
        if (subscriptionIndex !== -1) {
            setActiveSubscriptions(prev => [
                ...prev.slice(0, subscriptionIndex),
                ...prev.slice(subscriptionIndex + 1)
            ]);
        }
        
        return true;
    };

    // Unsubscribe from all topics
    const unsubscribeAll = () => {
        activeSubscriptions.forEach(sub => {
            mqttService.unsubscribe(sub.topic);
        });
        setActiveSubscriptions([]);
    };

    return (
        <MQTTContext.Provider value={{
            connectionStatus,
            marketData,
            activeSubscriptions,
            subscribeToStockInfo,
            subscribeToTopPrice,
            subscribeToTicks,
            subscribeToIndex,
            subscribeToOHLC,
            subscribeToBoardEvent,
            unsubscribe,
            unsubscribeAll,
            connectMQTT
        }}>
            {children}
        </MQTTContext.Provider>
    );
};

// Custom hook to use the MQTT context
export const useMQTT = () => {
    const context = useContext(MQTTContext);
    if (!context) {
        throw new Error('useMQTT must be used within an MQTTProvider');
    }
    return context;
};
