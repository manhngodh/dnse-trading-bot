import logging
from functools import wraps
from flask import jsonify
from ..exceptions import DNSEAPIError, TradingBotError

logger = logging.getLogger(__name__)

def handle_api_errors(func):
    """Decorator to handle API errors consistently"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DNSEAPIError as e:
            logger.error(f"DNSE API error in {func.__name__}: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e),
                'error_type': 'DNSE_API_ERROR'
            }), 400
        except TradingBotError as e:
            logger.error(f"Trading bot error in {func.__name__}: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e),
                'error_type': 'TRADING_BOT_ERROR'
            }), 400
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            return jsonify({
                'success': False,
                'error': "An unexpected error occurred",
                'error_type': 'INTERNAL_ERROR'
            }), 500
    return wrapper

def require_auth(func):
    """Decorator to check if client is authenticated"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        from flask import g
        if not g.client or not g.client.is_authenticated():
            return jsonify({
                'success': False,
                'error': 'Authentication required',
                'error_type': 'AUTH_ERROR'
            }), 401
        return func(*args, **kwargs)
    return wrapper

def require_trading_token(func):
    """Decorator to check if client has trading token"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        from flask import g
        if not g.client or not g.client.has_trading_token():
            return jsonify({
                'success': False,
                'error': 'Trading token required',
                'error_type': 'AUTH_ERROR'
            }), 401
        return func(*args, **kwargs)
    return wrapper
