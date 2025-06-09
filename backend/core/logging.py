import logging
import logging.handlers
import os
import sys
from datetime import datetime
from fastapi import Request

def setup_logging(app_name: str = 'dnse-trading-bot', log_level: str = 'INFO'):
    """
    Setup application logging with simple, readable logs and rotation
    
    Args:
        app_name: Name of the application
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Logger instance
    """
    # Create logs directory if it doesn't exist
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configure logging format
    log_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.getLevelName(log_level))
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(logs_dir, f'{app_name}.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)
    
    # Create logger for the application
    logger = logging.getLogger(app_name)
    
    return logger

# Request logging middleware for FastAPI
async def log_request_middleware(request: Request, call_next):
    """
    Middleware for logging HTTP requests and responses
    """
    logger = logging.getLogger("dnse-trading-bot")
    
    # Extract basic request information
    path = request.url.path
    method = request.method
    
    # Log request
    logger.info(f"Request: {method} {path}")
    
    # Process request and track timing
    start_time = datetime.now()
    try:
        response = await call_next(request)
        
        # Calculate response time
        process_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Log response
        logger.info(f"Response: {method} {path} - Status: {response.status_code} - Time: {process_time:.2f}ms")
        return response
    except Exception as e:
        # Log any exceptions
        logger.exception(f"Error processing {method} {path}: {str(e)}")
        raise
