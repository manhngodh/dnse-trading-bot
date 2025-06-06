import asyncio
import json
from typing import Dict, Any, Optional, Callable
import paho.mqtt.client as mqtt
from ..exceptions import DNSEAPIError

class MQTTChannel:
    def __init__(self):
        self.client = None
        self.callbacks: Dict[str, Callable] = {}
        self.investor_id: Optional[str] = None
        self.token: Optional[str] = None
        
    def initialize(self, investor_id: str, token: str):
        """Initialize MQTT client with credentials"""
        self.investor_id = investor_id
        self.token = token
        
        client_id = f"dnse-price-json-mqtt-ws-sub-{investor_id}"
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id,
            protocol=mqtt.MQTTv5,
            transport="websockets"
        )
        
        # Set credentials
        self.client.username_pw_set(self.investor_id, self.token)
        
        # Configure SSL/TLS
        self.client.tls_set(cert_reqs=ssl.CERT_NONE)
        self.client.tls_insecure_set(True)
        self.client.ws_set_options(path="/wss")
        
        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        
    def connect(self):
        """Connect to MQTT broker"""
        if not self.client:
            raise DNSEAPIError("MQTT client not initialized")
            
        try:
            self.client.connect("datafeed-lts-krx.dnse.com.vn", 443, keepalive=1200)
            self.client.loop_start()
        except Exception as e:
            raise DNSEAPIError(f"Failed to connect to MQTT broker: {str(e)}")
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.disconnect()
            self.client.loop_stop()
    
    def subscribe(self, symbol: str, callback: Callable):
        """Subscribe to market data for a symbol"""
        if not self.client:
            raise DNSEAPIError("MQTT client not initialized")
            
        topic = f"plaintext/quotes/krx/mdds/tick/v1/roundlot/symbol/{symbol}"
        self.callbacks[topic] = callback
        self.client.subscribe(topic, qos=1)
    
    def unsubscribe(self, symbol: str):
        """Unsubscribe from market data for a symbol"""
        if not self.client:
            raise DNSEAPIError("MQTT client not initialized")
            
        topic = f"plaintext/quotes/krx/mdds/tick/v1/roundlot/symbol/{symbol}"
        if topic in self.callbacks:
            del self.callbacks[topic]
        self.client.unsubscribe(topic)
    
    def _on_connect(self, client, userdata, flags, rc, properties):
        """Internal connect callback"""
        if rc == 0 and client.is_connected():
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect to MQTT broker, return code {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Internal message callback"""
        try:
            payload = json.loads(msg.payload.decode())
            if msg.topic in self.callbacks:
                self.callbacks[msg.topic](payload)
        except Exception as e:
            print(f"Error processing MQTT message: {str(e)}")

# Singleton instance
mqtt_channel = MQTTChannel()
