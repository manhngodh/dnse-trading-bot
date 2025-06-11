"""
Redis Configuration for DNSE Trading Bot
=======================================

This module provides Redis configuration and connection management
for the DNSE trading session manager.
"""

import redis
import logging
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("dnse-trading.redis")

class RedisConfig:
    """Redis configuration and connection manager"""
    
    def __init__(self):
        """Initialize Redis configuration"""
        self.redis_url = os.getenv(
            "REDIS_URL", 
            "redis://default:@173.249.7.24:6379/0"  # Default Redis URL, replace with your own
        )
        
        # Connection pool settings
        self.connection_settings = {
            "decode_responses": True,
            "socket_timeout": 30,
            "socket_connect_timeout": 30,
            "retry_on_timeout": True,
            "health_check_interval": 30,
            "max_connections": 20,
        }
        # Session settings
        self.session_prefix = "dnse_session"
        self.default_expire_seconds = 3600  # 1 hour
        self.max_expire_seconds = 28800     # 8 hours (max trading token validity)
        
    def create_connection(self) -> redis.Redis:
        """
        Create Redis connection with proper configuration
        
        Returns:
            Redis client instance
            
        Raises:
            Exception: If connection fails
        """
        try:
            client = redis.from_url(self.redis_url, **self.connection_settings)
            
            # Test connection
            client.ping()
            logger.info(f"Redis connection established to: {self._safe_url()}")
            
            return client
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def _safe_url(self) -> str:
        """Return safe URL for logging (without credentials)"""
        if '@' in self.redis_url:
            return self.redis_url.split('@')[1]
        return self.redis_url
    
    def get_session_key(self, session_id: str) -> str:
        """Get formatted session key"""
        return f"{self.session_prefix}:{session_id}"

# Global Redis configuration instance
redis_config = RedisConfig()
