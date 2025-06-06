import logging
import logging.handlers
import os

def setup_logging(app_name: str = 'dnse-trading-bot', log_level: str = 'INFO'):
    """Setup application logging"""
    
    # Create logs directory if it doesn't exist
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configure logging format
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.getLevelName(log_level))
    
    # Console handler
    console_handler = logging.StreamHandler()
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
    logger.setLevel(logging.getLevelName(log_level))
    
    return logger
