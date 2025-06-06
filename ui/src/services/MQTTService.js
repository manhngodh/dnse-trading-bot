import mqtt from 'mqtt';

class MQTTService {
    constructor() {
        this.client = null;
        this.listeners = {};
        this.subscriptions = new Set();
        this.connected = false;
        this.connecting = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.connectionCallbacks = [];
    }

    // Connect to the MQTT broker
    connect(investorId, token) {
        if (this.client || this.connecting) {
            return;
        }

        this.connecting = true;

        const clientId = `dnse-price-json-mqtt-ws-sub-${Math.floor(Math.random() * 1000) + 1000}`;
        const host = 'datafeed-lts-krx.dnse.com.vn';
        const port = 443;
        const path = '/wss';

        // Connection options
        const options = {
            clientId,
            username: investorId,
            password: token,
            protocol: 'wss',
            protocolVersion: 5,
            reconnectPeriod: 5000, // 5 seconds
            connectTimeout: 30000, // 30 seconds
            clean: true,
            rejectUnauthorized: false, // For self-signed certificates
            path
        };

        // Create and connect client
        this.client = mqtt.connect(`wss://${host}:${port}${path}`, options);

        // Set up event handlers
        this.client.on('connect', () => {
            console.log('Connected to MQTT broker');
            this.connected = true;
            this.connecting = false;
            this.reconnectAttempts = 0;
            
            // Resubscribe to previous topics if any
            this.resubscribe();
            
            // Notify listeners
            this.connectionCallbacks.forEach(cb => cb(true));
        });

        this.client.on('error', (error) => {
            console.error('MQTT connection error:', error);
            this.connecting = false;
            
            // Notify listeners
            this.connectionCallbacks.forEach(cb => cb(false, error));
        });

        this.client.on('disconnect', () => {
            console.log('Disconnected from MQTT broker');
            this.connected = false;
            
            // Notify listeners
            this.connectionCallbacks.forEach(cb => cb(false));
        });

        this.client.on('offline', () => {
            console.log('MQTT client is offline');
            this.connected = false;
            
            // Notify listeners
            this.connectionCallbacks.forEach(cb => cb(false));
        });

        this.client.on('reconnect', () => {
            console.log('Attempting to reconnect to MQTT broker...');
            this.reconnectAttempts++;
            
            if (this.reconnectAttempts > this.maxReconnectAttempts) {
                console.error('Max reconnect attempts reached');
                this.client.end();
                
                // Notify listeners
                this.connectionCallbacks.forEach(cb => cb(false, new Error('Max reconnect attempts reached')));
            }
        });

        this.client.on('message', (topic, message) => {
            try {
                const payload = JSON.parse(message.toString());
                
                // Check if we have listeners for this topic
                if (this.listeners[topic]) {
                    this.listeners[topic].forEach(callback => {
                        callback(payload, topic);
                    });
                }
            } catch (error) {
                console.error('Error parsing MQTT message:', error);
            }
        });

        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error('Connection timeout'));
                this.connecting = false;
            }, options.connectTimeout);

            this.client.once('connect', () => {
                clearTimeout(timeout);
                resolve();
            });

            this.client.once('error', (err) => {
                clearTimeout(timeout);
                reject(err);
                this.connecting = false;
            });
        });
    }

    // Disconnect from the MQTT broker
    disconnect() {
        if (this.client) {
            this.client.end(true);
            this.client = null;
            this.connected = false;
            this.subscriptions.clear();
            this.listeners = {};
            console.log('Disconnected from MQTT broker');
        }
    }

    // Add connection status callback
    onConnectionChange(callback) {
        this.connectionCallbacks.push(callback);
        return () => {
            this.connectionCallbacks = this.connectionCallbacks.filter(cb => cb !== callback);
        };
    }

    // Subscribe to a topic
    subscribe(topic, callback) {
        if (!this.client || !this.connected) {
            console.error('MQTT client not connected');
            return false;
        }

        // Add to subscriptions set
        this.subscriptions.add(topic);

        // Set up listener
        if (!this.listeners[topic]) {
            this.listeners[topic] = [];
        }
        this.listeners[topic].push(callback);

        // Subscribe to the topic
        this.client.subscribe(topic, { qos: 1 }, (error) => {
            if (error) {
                console.error(`Error subscribing to ${topic}:`, error);
                return false;
            }
            console.log(`Subscribed to ${topic}`);
        });

        return true;
    }

    // Unsubscribe from a topic
    unsubscribe(topic, callback) {
        if (!this.client || !this.connected) {
            console.error('MQTT client not connected');
            return;
        }

        // If a specific callback is provided, only remove that callback
        if (callback && this.listeners[topic]) {
            this.listeners[topic] = this.listeners[topic].filter(cb => cb !== callback);
            
            // If no more listeners for this topic, unsubscribe
            if (this.listeners[topic].length === 0) {
                this.client.unsubscribe(topic);
                delete this.listeners[topic];
                this.subscriptions.delete(topic);
                console.log(`Unsubscribed from ${topic}`);
            }
        } else {
            // Remove all listeners for this topic
            this.client.unsubscribe(topic);
            delete this.listeners[topic];
            this.subscriptions.delete(topic);
            console.log(`Unsubscribed from ${topic}`);
        }
    }

    // Resubscribe to all previously subscribed topics (used after reconnection)
    resubscribe() {
        if (!this.client || !this.connected) {
            return;
        }

        this.subscriptions.forEach(topic => {
            this.client.subscribe(topic, { qos: 1 }, (error) => {
                if (error) {
                    console.error(`Error resubscribing to ${topic}:`, error);
                } else {
                    console.log(`Resubscribed to ${topic}`);
                }
            });
        });
    }

    // Build topic strings for different market data types
    static buildTopics = {
        stockInfo: (symbol) => `plaintext/quotes/krx/mdds/stockinfo/v1/roundlot/symbol/${symbol}`,
        topPrice: (symbol) => `plaintext/quotes/krx/mdds/topprice/v1/roundlot/symbol/${symbol}`,
        boardEvent: (market, productGrpId) => `plaintext/quotes/krx/mdds/boardevent/v1/roundlot/market/${market}/product/${productGrpId}`,
        marketIndex: (indexName) => `plaintext/quotes/krx/mdds/index/${indexName}`,
        stockOHLC: (resolution, symbol) => `plaintext/quotes/krx/mdds/v2/ohlc/stock/${resolution}/${symbol}`,
        derivativeOHLC: (resolution, symbol) => `plaintext/quotes/krx/mdds/v2/ohlc/derivative/${resolution}/${symbol}`,
        indexOHLC: (resolution, indexName) => `plaintext/quotes/krx/mdds/v2/ohlc/index/${resolution}/${indexName}`,
        tick: (symbol) => `plaintext/quotes/krx/mdds/tick/v1/roundlot/symbol/${symbol}`
    };
}

// Create a singleton instance
const mqttService = new MQTTService();
export default mqttService;
