import os
from typing import Dict, Any

class Config:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # DNSE API URLs
    DNSE_USER_SERVICE = 'https://api.dnse.com.vn/user-service'
    DNSE_AUTH_SERVICE = 'https://api.dnse.com.vn/auth-service'
    DNSE_ORDER_SERVICE = 'https://api.dnse.com.vn/order-service'
    
    # MQTT Settings
    MQTT_BROKER_HOST = "datafeed-lts-krx.dnse.com.vn"
    MQTT_BROKER_PORT = 443
    MQTT_CLIENT_ID_PREFIX = "dnse-price-json-mqtt-ws-sub-"
    
    # Cache Settings
    MARKET_DATA_CACHE_TTL = 5  # seconds
    PORTFOLIO_CACHE_TTL = 30  # seconds
    
    @staticmethod
    def to_dict() -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {k: v for k, v in Config.__dict__.items() 
                if not k.startswith('_') and k.isupper()}

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    ENV = 'production'
    DEBUG = False
    # Override these with secure values in production
    SECRET_KEY = os.getenv('SECRET_KEY')

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    ENV = 'testing'

# Configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

# Active configuration
active_config = config_by_name[os.getenv('FLASK_ENV', 'development')]
