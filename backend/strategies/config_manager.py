# Configuration Management for Grid Trading Bot
import json
import os
from decimal import Decimal
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Manages configuration loading, validation, and updates for the grid trading bot
    """
    
    DEFAULT_CONFIG = {
        "api": {
            "username": "",
            "password": "",
            "base_url": "https://api.dnse.com.vn",
            "mqtt_host": "datafeed-lts-krx.dnse.com.vn",
            "mqtt_port": 443,
            "timeout": 15,
            "retry_attempts": 3
        },
        "strategy": {
            "symbol": "HPG",
            "account_no": "",
            "loan_package_id": None,
            "grid_mode": "recursive",
            "grid_levels": 8,
            "grid_spacing_pct": 0.02,
            "grid_span_pct": 0.16,
            "initial_qty_pct": 0.08,
            "ddown_factor": 1.5,
            "max_position_size": 5000,
            "min_markup_pct": 0.005,
            "markup_range_pct": 0.015,
            "wallet_exposure_limit_pct": 0.25,
            "max_drawdown_pct": 0.08,
            "stop_loss_pct": None,
            "ema_span_0": 12,
            "ema_span_1": 26,
            "use_ema_smoothing": True,
            "price_precision": 0,
            "min_order_value": 100000
        },
        "risk": {
            "max_daily_loss": 1000000,  # 1M VND
            "max_open_orders": 20,
            "position_size_limit": 0.5,  # 50% of capital
            "emergency_stop_enabled": True,
            "emergency_stop_loss_pct": 0.15  # 15% portfolio loss
        },
        "operational": {
            "monitoring_interval": 5,
            "log_level": "INFO",
            "log_file": "grid_bot.log",
            "enable_market_data_stream": True,
            "market_data_fallback": True,
            "fallback_update_interval": 10,
            "dry_run": False,
            "auto_restart": False,
            "max_restart_attempts": 3
        },
        "notifications": {
            "enabled": False,
            "email": {
                "enabled": False,
                "smtp_server": "",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "to_address": ""
            },
            "webhook": {
                "enabled": False,
                "url": "",
                "events": ["trade", "error", "stop"]
            }
        }
    }
    
    def __init__(self, config_file: str = "grid_bot_config.json"):
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}
        self.validation_errors: List[str] = []
    
    def load_config(self) -> bool:
        """Load configuration from file"""
        try:
            if not self.config_file.exists():
                logger.info(f"Config file {self.config_file} not found. Creating default configuration...")
                self.create_default_config()
                return False
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            # Merge with defaults to ensure all required keys exist
            self.config = self._merge_configs(self.DEFAULT_CONFIG, loaded_config)
            
            # Load environment variable overrides
            self._load_env_overrides()
            
            # Validate configuration
            if not self.validate_config():
                logger.error(f"Configuration validation failed: {', '.join(self.validation_errors)}")
                return False
            
            logger.info(f"Configuration loaded successfully from {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return False
    
    def create_default_config(self) -> None:
        """Create a default configuration file"""
        try:
            # Add helpful comments to the default config
            config_with_comments = {
                "_comments": {
                    "api": "DNSE API credentials and connection settings",
                    "strategy": "Grid trading strategy parameters",
                    "risk": "Risk management settings",
                    "operational": "Bot operational settings",
                    "notifications": "Alert and notification settings"
                },
                **self.DEFAULT_CONFIG
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_with_comments, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Default configuration created at {self.config_file}")
            logger.info("Please update the configuration with your DNSE credentials and trading parameters")
            
        except Exception as e:
            logger.error(f"Error creating default configuration: {e}")
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge user config with default config"""
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _load_env_overrides(self) -> None:
        """Load configuration overrides from environment variables"""
        env_mappings = {
            'DNSE_USERNAME': ('api', 'username'),
            'DNSE_PASSWORD': ('api', 'password'),
            'DNSE_ACCOUNT_NO': ('strategy', 'account_no'),
            'GRID_SYMBOL': ('strategy', 'symbol'),
            'GRID_LEVELS': ('strategy', 'grid_levels'),
            'GRID_SPACING': ('strategy', 'grid_spacing_pct'),
            'DRY_RUN': ('operational', 'dry_run'),
            'LOG_LEVEL': ('operational', 'log_level')
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert types appropriately
                if key in ['grid_levels', 'mqtt_port', 'timeout', 'retry_attempts']:
                    value = int(value)
                elif key in ['grid_spacing_pct', 'initial_qty_pct', 'ddown_factor']:
                    value = float(value)
                elif key in ['dry_run', 'enable_market_data_stream', 'auto_restart']:
                    value = value.lower() in ('true', '1', 'yes', 'on')
                
                self.config[section][key] = value
                logger.debug(f"Override from environment: {section}.{key} = {value}")
    
    def validate_config(self) -> bool:
        """Validate the loaded configuration"""
        self.validation_errors = []
        
        # Validate API configuration
        self._validate_api_config()
        
        # Validate strategy configuration
        self._validate_strategy_config()
        
        # Validate risk configuration
        self._validate_risk_config()
        
        # Validate operational configuration
        self._validate_operational_config()
        
        return len(self.validation_errors) == 0
    
    def _validate_api_config(self) -> None:
        """Validate API configuration"""
        api_config = self.config.get('api', {})
        
        # Check for required credentials (unless in dry run mode)
        if not self.config.get('operational', {}).get('dry_run', False):
            if not api_config.get('username'):
                self.validation_errors.append("API username is required")
            if not api_config.get('password'):
                self.validation_errors.append("API password is required")
        
        # Validate timeout and retry settings
        if api_config.get('timeout', 0) <= 0:
            self.validation_errors.append("API timeout must be positive")
        if api_config.get('retry_attempts', 0) < 0:
            self.validation_errors.append("Retry attempts must be non-negative")
    
    def _validate_strategy_config(self) -> None:
        """Validate strategy configuration"""
        strategy_config = self.config.get('strategy', {})
        
        # Required fields
        if not strategy_config.get('symbol'):
            self.validation_errors.append("Trading symbol is required")
        
        # Validate numeric ranges
        if strategy_config.get('grid_levels', 0) < 2:
            self.validation_errors.append("Grid levels must be at least 2")
        
        if not (0 < strategy_config.get('grid_spacing_pct', 0) <= 0.1):
            self.validation_errors.append("Grid spacing must be between 0 and 10%")
        
        if not (0 < strategy_config.get('initial_qty_pct', 0) <= 1):
            self.validation_errors.append("Initial quantity percentage must be between 0 and 100%")
        
        if strategy_config.get('ddown_factor', 0) < 1:
            self.validation_errors.append("DCA factor must be >= 1")
        
        if strategy_config.get('max_position_size', 0) <= 0:
            self.validation_errors.append("Maximum position size must be positive")
        
        if not (0 <= strategy_config.get('wallet_exposure_limit_pct', 0) <= 1):
            self.validation_errors.append("Wallet exposure limit must be between 0 and 100%")
    
    def _validate_risk_config(self) -> None:
        """Validate risk management configuration"""
        risk_config = self.config.get('risk', {})
        
        if risk_config.get('max_daily_loss', 0) <= 0:
            self.validation_errors.append("Maximum daily loss must be positive")
        
        if risk_config.get('max_open_orders', 0) <= 0:
            self.validation_errors.append("Maximum open orders must be positive")
        
        if not (0 < risk_config.get('position_size_limit', 0) <= 1):
            self.validation_errors.append("Position size limit must be between 0 and 100%")
    
    def _validate_operational_config(self) -> None:
        """Validate operational configuration"""
        op_config = self.config.get('operational', {})
        
        if op_config.get('monitoring_interval', 0) <= 0:
            self.validation_errors.append("Monitoring interval must be positive")
        
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if op_config.get('log_level', 'INFO') not in valid_log_levels:
            self.validation_errors.append(f"Log level must be one of: {', '.join(valid_log_levels)}")
    
    def get_config(self) -> Dict[str, Any]:
        """Get the complete configuration"""
        return self.config.copy()
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get a specific configuration section"""
        return self.config.get(section, {}).copy()
    
    def get_value(self, section: str, key: str, default: Any = None) -> Any:
        """Get a specific configuration value"""
        return self.config.get(section, {}).get(key, default)
    
    def update_value(self, section: str, key: str, value: Any) -> None:
        """Update a configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
    
    def save_config(self) -> bool:
        """Save the current configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get_validation_errors(self) -> List[str]:
        """Get configuration validation errors"""
        return self.validation_errors.copy()
    
    def print_config_summary(self) -> None:
        """Print a summary of the current configuration"""
        strategy_config = self.get_section('strategy')
        
        print("\n=== Grid Trading Bot Configuration ===")
        print(f"Symbol: {strategy_config.get('symbol')}")
        print(f"Grid Mode: {strategy_config.get('grid_mode')}")
        print(f"Grid Levels: {strategy_config.get('grid_levels')}")
        print(f"Grid Spacing: {strategy_config.get('grid_spacing_pct', 0) * 100:.1f}%")
        print(f"Initial Quantity: {strategy_config.get('initial_qty_pct', 0) * 100:.1f}%")
        print(f"Max Position: {strategy_config.get('max_position_size'):,}")
        print(f"Wallet Exposure Limit: {strategy_config.get('wallet_exposure_limit_pct', 0) * 100:.1f}%")
        
        op_config = self.get_section('operational')
        print(f"Dry Run: {op_config.get('dry_run', False)}")
        print(f"Market Data Stream: {op_config.get('enable_market_data_stream', True)}")
        print("=====================================\n")
