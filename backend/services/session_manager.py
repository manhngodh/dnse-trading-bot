"""
Redis Session Manager for DNSE Trading Bot
==========================================

This module provides Redis-based session management for storing authentication
tokens and session data for the DNSE trading client.
"""

import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dotenv import load_dotenv
from core.redis_config import redis_config

load_dotenv()

logger = logging.getLogger("dnse-trading.session")

class SessionManager:
    """Redis-based session manager for DNSE trading authentication"""
    
    _instance = None
    _redis_client = None
    _session_prefix = None
    _default_expire_seconds = None
    _max_expire_seconds = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            try:
                # Initialize Redis connection only once
                cls._redis_client = redis_config.create_connection()
                cls._session_prefix = redis_config.session_prefix
                cls._default_expire_seconds = redis_config.default_expire_seconds
                cls._max_expire_seconds = redis_config.max_expire_seconds
                logger.info("SessionManager singleton initialized")
            except Exception as e:
                logger.error(f"Failed to initialize SessionManager singleton: {e}")
                raise
        return cls._instance

    def __init__(self):
        """No need to initialize anything here since it's handled in __new__"""
        pass

    @property
    def redis_client(self):
        return self._redis_client

    @property
    def session_prefix(self):
        return self._session_prefix

    @property
    def default_expire_seconds(self):
        return self._default_expire_seconds

    @property
    def max_expire_seconds(self):
        return self._max_expire_seconds
    
    def create_session(self, session_id: str, session_data: Dict[str, Any], expire_seconds: int = None) -> bool:
        """
        Create a new session in Redis
        
        Args:
            session_id: Unique session identifier
            session_data: Session data to store
            expire_seconds: Session expiration time in seconds (default from config)
            
        Returns:
            True if session created successfully
        """
        try:
            if expire_seconds is None:
                expire_seconds = self.default_expire_seconds
                
            session_key = redis_config.get_session_key(session_id)
            
            # Add timestamp
            session_data["created_at"] = datetime.now().isoformat()
            session_data["expires_at"] = (datetime.now() + timedelta(seconds=expire_seconds)).isoformat()
            
            # Store session data
            self.redis_client.setex(
                session_key,
                expire_seconds,
                json.dumps(session_data, ensure_ascii=False)
            )
            
            logger.info(f"Session created: {session_id} (expires in {expire_seconds}s)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create session {session_id}: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data from Redis
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data dictionary or None if not found
        """
        try:
            session_key = redis_config.get_session_key(session_id)
            session_data = self.redis_client.get(session_key)
            
            if session_data:
                logger.debug(f"Session retrieved: {session_id}")
                return json.loads(session_data)
            
            logger.debug(f"Session not found: {session_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None
    
    def update_session(self, session_id: str, updates: Dict[str, Any], extend_ttl: bool = True) -> bool:
        """
        Update session data
        
        Args:
            session_id: Session identifier
            updates: Data to update
            extend_ttl: Whether to extend session TTL
            
        Returns:
            True if update successful
        """
        try:
            session_key = redis_config.get_session_key(session_id)
            
            # Get current session data
            current_data = self.get_session(session_id)
            if not current_data:
                logger.warning(f"Cannot update non-existent session: {session_id}")
                return False
            
            # Update data
            current_data.update(updates)
            current_data["updated_at"] = datetime.now().isoformat()
            
            # Determine TTL
            ttl = self.default_expire_seconds
            if extend_ttl:
                current_ttl = self.redis_client.ttl(session_key)
                if current_ttl > 0:
                    ttl = max(current_ttl, self.default_expire_seconds)
                else:
                    ttl = self.default_expire_seconds
            
            # Store updated data
            self.redis_client.setex(
                session_key,
                ttl,
                json.dumps(current_data, ensure_ascii=False)
            )
            
            logger.info(f"Session updated: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update session {session_id}: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete session from Redis
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deletion successful
        """
        try:
            session_key = redis_config.get_session_key(session_id)
            result = self.redis_client.delete(session_key)
            
            if result:
                logger.info(f"Session deleted: {session_id}")
                return True
            else:
                logger.warning(f"Session not found for deletion: {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False
    
    def extend_session(self, session_id: str, expire_seconds: int = None) -> bool:
        """
        Extend session TTL
        
        Args:
            session_id: Session identifier
            expire_seconds: New expiration time in seconds (default from config)
            
        Returns:
            True if extension successful
        """
        try:
            if expire_seconds is None:
                expire_seconds = self.default_expire_seconds
                
            session_key = redis_config.get_session_key(session_id)
            result = self.redis_client.expire(session_key, expire_seconds)
            
            if result:
                logger.debug(f"Session TTL extended: {session_id} (+{expire_seconds}s)")
                return True
            else:
                logger.warning(f"Session not found for TTL extension: {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to extend session {session_id}: {e}")
            return False
    
    def get_session_ttl(self, session_id: str) -> int:
        """
        Get remaining TTL for session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Remaining TTL in seconds, -1 if session doesn't exist
        """
        try:
            session_key = redis_config.get_session_key(session_id)
            return self.redis_client.ttl(session_key)
        except Exception as e:
            logger.error(f"Failed to get TTL for session {session_id}: {e}")
            return -1
    
    def list_sessions(self, pattern: str = None) -> List[str]:
        """
        List all sessions matching pattern
        
        Args:
            pattern: Redis key pattern (default: all DNSE sessions)
            
        Returns:
            List of session IDs
        """
        try:
            if pattern is None:
                pattern = f"{self.session_prefix}:*"
                
            keys = self.redis_client.keys(pattern)
            # Extract session IDs from keys
            session_ids = [key.replace(f"{self.session_prefix}:", "") for key in keys]
            return session_ids
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return []
    
    def cleanup_expired_sessions(self) -> int:
        """
        Cleanup expired sessions (Redis handles this automatically with TTL)
        This method is mainly for monitoring/logging purposes
        
        Returns:
            Number of active sessions
        """
        try:
            active_sessions = self.list_sessions()
            logger.info(f"Active sessions: {len(active_sessions)}")
            return len(active_sessions)
        except Exception as e:
            logger.error(f"Failed to cleanup sessions: {e}")
            return 0
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get session information including TTL and basic data
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with session info
        """
        try:
            session_data = self.get_session(session_id)
            if not session_data:
                return {"exists": False}
            
            ttl = self.get_session_ttl(session_id)
            
            return {
                "exists": True,
                "ttl": ttl,
                "created_at": session_data.get("created_at"),
                "updated_at": session_data.get("updated_at"),
                "authenticated": session_data.get("authenticated", False),
                "otp_verified": session_data.get("otp_verified", False),
                "has_accounts": bool(session_data.get("accounts")),
                "investor_id": session_data.get("investor_info", {}).get("investorId") if session_data.get("investor_info") else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get session info for {session_id}: {e}")
            return {"exists": False, "error": str(e)}
