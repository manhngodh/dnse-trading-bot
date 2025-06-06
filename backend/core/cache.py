import time
import json
from typing import Dict, Any

class Cache:
    """Simple in-memory cache with expiration"""
    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.expiry: Dict[str, float] = {}
    
    def get(self, key: str) -> Any:
        """Get value from cache if not expired"""
        if key in self.cache and time.time() < self.expiry[key]:
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = 60):
        """Set value in cache with TTL in seconds"""
        self.cache[key] = value
        self.expiry[key] = time.time() + ttl
    
    def delete(self, key: str):
        """Delete value from cache"""
        if key in self.cache:
            del self.cache[key]
            del self.expiry[key]
            
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        self.expiry.clear()

# Global cache instance
market_data_cache = Cache()
portfolio_cache = Cache()
