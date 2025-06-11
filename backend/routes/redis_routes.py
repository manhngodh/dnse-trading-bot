"""
Redis Health Check and Monitoring Routes
======================================

FastAPI routes for Redis health monitoring and session management.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import logging
from core.redis_config import redis_config
from core.redis_utils import redis_session_store
from services.session_manager import SessionManager

logger = logging.getLogger("dnse-trading.redis_routes")

router = APIRouter(prefix="/redis", tags=["redis"])

@router.get("/health", response_model=Dict[str, Any])
async def redis_health_check():
    """
    Check Redis connection health
    
    Returns:
        Redis health status and basic info
    """
    try:
        # Test Redis connection
        client = redis_config.create_connection()
        
        # Ping Redis
        ping_result = client.ping()
        
        # Get server info
        info = client.info()
        
        health_data = {
            "status": "healthy" if ping_result else "unhealthy",
            "connected": ping_result,
            "redis_version": info.get("redis_version", "unknown"),
            "used_memory": info.get("used_memory_human", "unknown"),
            "connected_clients": info.get("connected_clients", 0),
            "total_connections_received": info.get("total_connections_received", 0),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "uptime_in_seconds": info.get("uptime_in_seconds", 0)
        }
        
        # Calculate hit rate
        hits = health_data["keyspace_hits"]
        misses = health_data["keyspace_misses"]
        if hits + misses > 0:
            health_data["hit_rate"] = f"{(hits / (hits + misses)) * 100:.2f}%"
        else:
            health_data["hit_rate"] = "N/A"
        
        logger.info("Redis health check completed successfully")
        return health_data
        
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Redis health check failed: {str(e)}"
        )

@router.get("/sessions/stats", response_model=Dict[str, Any])
async def get_session_statistics():
    """
    Get Redis session statistics
    
    Returns:
        Session statistics and metrics
    """
    try:
        stats = redis_session_store.get_session_statistics()
        logger.info("Session statistics retrieved successfully")
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get session statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session statistics: {str(e)}"
        )

@router.get("/sessions/list", response_model=List[str])
async def list_active_sessions():
    """
    List all active sessions
    
    Returns:
        List of active session IDs
    """
    try:
        session_manager = SessionManager()
        sessions = session_manager.list_sessions()
        
        logger.info(f"Listed {len(sessions)} active sessions")
        return sessions
        
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list sessions: {str(e)}"
        )

@router.get("/sessions/{session_id}", response_model=Dict[str, Any])
async def get_session_info(session_id: str):
    """
    Get detailed information about a specific session
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session information and metadata
    """
    try:
        session_manager = SessionManager()
        session_info = session_manager.get_session_info(session_id)
        
        if not session_info.get("exists", False):
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        logger.info(f"Session info retrieved for: {session_id}")
        return session_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session info for {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session info: {str(e)}"
        )

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a specific session
    
    Args:
        session_id: Session identifier
        
    Returns:
        Deletion status
    """
    try:
        session_manager = SessionManager()
        success = session_manager.delete_session(session_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found or already deleted"
            )
        
        logger.info(f"Session deleted: {session_id}")
        return {"message": f"Session {session_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete session: {str(e)}"
        )

@router.post("/sessions/{session_id}/extend")
async def extend_session(session_id: str, expire_seconds: int = None):
    """
    Extend session TTL
    
    Args:
        session_id: Session identifier
        expire_seconds: New expiration time in seconds
        
    Returns:
        Extension status
    """
    try:
        session_manager = SessionManager()
        success = session_manager.extend_session(session_id, expire_seconds)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        ttl = expire_seconds or session_manager.default_expire_seconds
        logger.info(f"Session {session_id} extended by {ttl} seconds")
        return {"message": f"Session {session_id} extended successfully", "ttl": ttl}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to extend session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extend session: {str(e)}"
        )

@router.post("/cleanup")
async def cleanup_expired_data():
    """
    Clean up expired Redis data
    
    Returns:
        Cleanup statistics
    """
    try:
        cleanup_stats = redis_session_store.cleanup_expired_data()
        
        logger.info(f"Redis cleanup completed: {cleanup_stats}")
        return {
            "message": "Cleanup completed successfully",
            "statistics": cleanup_stats
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup expired data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup expired data: {str(e)}"
        )

@router.get("/config", response_model=Dict[str, Any])
async def get_redis_config():
    """
    Get Redis configuration information
    
    Returns:
        Redis configuration details (safe for display)
    """
    try:
        config_info = {
            "session_prefix": redis_config.session_prefix,
            "default_expire_seconds": redis_config.default_expire_seconds,
            "max_expire_seconds": redis_config.max_expire_seconds,
            "connection_settings": {
                "socket_timeout": redis_config.connection_settings["socket_timeout"],
                "socket_connect_timeout": redis_config.connection_settings["socket_connect_timeout"],
                "max_connections": redis_config.connection_settings["max_connections"],
                "health_check_interval": redis_config.connection_settings["health_check_interval"]
            },
            "redis_url_host": redis_config._safe_url()
        }
        
        logger.info("Redis configuration retrieved successfully")
        return config_info
        
    except Exception as e:
        logger.error(f"Failed to get Redis configuration: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get Redis configuration: {str(e)}"
        )
