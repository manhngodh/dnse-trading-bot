"""
Redis Utilities for DNSE Trading Bot
===================================

Additional Redis utilities for session management and caching.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from core.redis_config import redis_config

logger = logging.getLogger("dnse-trading.redis_utils")

class RedisSessionStore:
    """Advanced Redis session store with additional features"""
    
    def __init__(self):
        """Initialize Redis session store"""
        self.redis_client = redis_config.create_connection()
        self.session_prefix = redis_config.session_prefix
        
    def store_trading_state(self, session_id: str, trading_data: Dict[str, Any]) -> bool:
        """
        Store trading state (positions, orders, etc.) in Redis
        
        Args:
            session_id: Session identifier
            trading_data: Trading state data
            
        Returns:
            True if successful
        """
        try:
            key = f"{self.session_prefix}:trading:{session_id}"
            
            # Add timestamp
            trading_data["last_updated"] = datetime.now().isoformat()
            
            # Store with shorter TTL for trading data (30 minutes)
            self.redis_client.setex(
                key,
                1800,  # 30 minutes
                json.dumps(trading_data, ensure_ascii=False)
            )
            
            logger.debug(f"Trading state stored for session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store trading state for {session_id}: {e}")
            return False
    
    def get_trading_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get trading state from Redis
        
        Args:
            session_id: Session identifier
            
        Returns:
            Trading state data or None
        """
        try:
            key = f"{self.session_prefix}:trading:{session_id}"
            data = self.redis_client.get(key)
            
            if data:
                return json.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get trading state for {session_id}: {e}")
            return None
    
    def cache_market_data(self, symbol: str, market_data: Dict[str, Any], ttl: int = 60) -> bool:
        """
        Cache market data in Redis
        
        Args:
            symbol: Stock symbol
            market_data: Market data to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        try:
            key = f"market_data:{symbol}"
            
            # Add timestamp
            market_data["cached_at"] = datetime.now().isoformat()
            
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(market_data, ensure_ascii=False)
            )
            
            logger.debug(f"Market data cached for {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache market data for {symbol}: {e}")
            return False
    
    def get_cached_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get cached market data
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Cached market data or None
        """
        try:
            key = f"market_data:{symbol}"
            data = self.redis_client.get(key)
            
            if data:
                return json.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get cached market data for {symbol}: {e}")
            return None
    
    def store_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Store user preferences in Redis
        
        Args:
            user_id: User identifier
            preferences: User preferences
            
        Returns:
            True if successful
        """
        try:
            key = f"user_prefs:{user_id}"
            
            # Store with longer TTL (24 hours)
            self.redis_client.setex(
                key,
                86400,  # 24 hours
                json.dumps(preferences, ensure_ascii=False)
            )
            
            logger.debug(f"User preferences stored for: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store user preferences for {user_id}: {e}")
            return False
    
    def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user preferences from Redis
        
        Args:
            user_id: User identifier
            
        Returns:
            User preferences or None
        """
        try:
            key = f"user_prefs:{user_id}"
            data = self.redis_client.get(key)
            
            if data:
                return json.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user preferences for {user_id}: {e}")
            return None
    
    def increment_api_calls(self, endpoint: str, window_seconds: int = 3600) -> int:
        """
        Increment API call counter for rate limiting
        
        Args:
            endpoint: API endpoint name
            window_seconds: Time window in seconds
            
        Returns:
            Current count
        """
        try:
            key = f"api_calls:{endpoint}:{datetime.now().strftime('%Y%m%d%H')}"
            
            # Increment counter
            count = self.redis_client.incr(key)
            
            # Set expiration on first increment
            if count == 1:
                self.redis_client.expire(key, window_seconds)
            
            return count
            
        except Exception as e:
            logger.error(f"Failed to increment API calls for {endpoint}: {e}")
            return 0
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """
        Get Redis session statistics
        
        Returns:
            Dictionary with session stats
        """
        try:
            # Get all session keys
            session_keys = self.redis_client.keys(f"{self.session_prefix}:*")
            
            # Filter out trading and other sub-keys
            main_sessions = [k for k in session_keys if k.count(':') == 1]
            
            # Get memory usage info
            info = self.redis_client.info('memory')
            
            stats = {
                "total_sessions": len(main_sessions),
                "active_sessions": len([k for k in main_sessions if self.redis_client.ttl(k) > 0]),
                "memory_used": info.get('used_memory_human', 'N/A'),
                "connected_clients": self.redis_client.info('clients').get('connected_clients', 0),
                "keyspace_hits": self.redis_client.info('stats').get('keyspace_hits', 0),
                "keyspace_misses": self.redis_client.info('stats').get('keyspace_misses', 0)
            }
            
            # Calculate hit rate
            hits = stats['keyspace_hits']
            misses = stats['keyspace_misses']
            if hits + misses > 0:
                stats['hit_rate'] = f"{(hits / (hits + misses)) * 100:.2f}%"
            else:
                stats['hit_rate'] = "N/A"
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get session statistics: {e}")
            return {}
    
    def cleanup_expired_data(self) -> Dict[str, int]:
        """
        Clean up expired data and return cleanup stats
        
        Returns:
            Dictionary with cleanup statistics
        """
        try:
            cleaned = {
                "sessions": 0,
                "trading_data": 0,
                "market_data": 0,
                "user_prefs": 0
            }
            
            # Clean expired sessions (Redis handles TTL automatically, this is for monitoring)
            session_keys = self.redis_client.keys(f"{self.session_prefix}:*")
            for key in session_keys:
                ttl = self.redis_client.ttl(key)
                if ttl == -2:  # Key doesn't exist (expired)
                    if ":trading:" in key:
                        cleaned["trading_data"] += 1
                    elif key.count(':') == 1:
                        cleaned["sessions"] += 1
            
            # Clean expired market data
            market_keys = self.redis_client.keys("market_data:*")
            for key in market_keys:
                if self.redis_client.ttl(key) == -2:
                    cleaned["market_data"] += 1
            
            # Clean expired user preferences
            pref_keys = self.redis_client.keys("user_prefs:*")
            for key in pref_keys:
                if self.redis_client.ttl(key) == -2:
                    cleaned["user_prefs"] += 1
            
            logger.info(f"Cleanup completed: {cleaned}")
            return cleaned
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired data: {e}")
            return {}

# Global Redis session store instance
redis_session_store = RedisSessionStore()
