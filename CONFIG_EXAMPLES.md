# DNSE Grid Trading Bot - Example Configuration

This is an example configuration file that shows all available parameters for the grid trading bot.

## Quick Setup

1. Copy this file to `grid_bot_config.json`
2. Edit the `api` section with your DNSE credentials
3. Adjust strategy parameters as needed
4. Run: `python run_grid_bot.py --dry-run` to test

## Configuration Sections

### API Configuration
```json
{
  "api": {
    "username": "your_email@example.com",     // Your DNSE login email
    "password": "your_password",              // Your DNSE password
    "base_url": "https://api.dnse.com.vn",    // DNSE API base URL
    "mqtt_host": "datafeed-lts-krx.dnse.com.vn", // Market data host
    "mqtt_port": 443,                         // Market data port
    "timeout": 15,                            // API timeout in seconds
    "retry_attempts": 3                       // API retry attempts
  }
}
```

### Strategy Configuration
```json
{
  "strategy": {
    "symbol": "HPG",                    // Trading symbol (e.g., HPG, VIC, VCB)
    "account_no": "",                   // Leave empty - auto-detected
    "loan_package_id": null,            // Margin loan package (optional)
    "grid_mode": "recursive",           // Grid mode: "recursive" only for now
    "grid_levels": 8,                   // Number of grid levels (2-20)
    "grid_spacing_pct": 0.02,          // 2% spacing between levels
    "grid_span_pct": 0.16,             // Total grid span percentage
    "initial_qty_pct": 0.08,           // 8% of capital per initial order
    "ddown_factor": 1.5,               // DCA multiplier (1.0-3.0)
    "max_position_size": 5000,         // Maximum total shares
    "min_markup_pct": 0.005,           // 0.5% minimum take profit
    "markup_range_pct": 0.015,         // 1.5% markup range
    "wallet_exposure_limit_pct": 0.25, // 25% max capital exposure
    "max_drawdown_pct": 0.08,          // 8% max drawdown before stop
    "stop_loss_pct": null,             // Position stop loss (optional)
    "ema_span_0": 12,                  // Fast EMA period
    "ema_span_1": 26,                  // Slow EMA period
    "use_ema_smoothing": true,         // Enable EMA smoothing
    "price_precision": 0,              // Price decimal places (0 for VN stocks)
    "min_order_value": 100000          // Minimum order value (100k VND)
  }
}
```

### Risk Management
```json
{
  "risk": {
    "max_daily_loss": 1000000,         // 1M VND max daily loss
    "max_open_orders": 20,             // Maximum open orders
    "position_size_limit": 0.5,        // 50% max position size
    "emergency_stop_enabled": true,     // Enable emergency stops
    "emergency_stop_loss_pct": 0.15    // 15% emergency stop loss
  }
}
```

### Operational Settings
```json
{
  "operational": {
    "monitoring_interval": 5,          // Status update interval (seconds)
    "log_level": "INFO",              // DEBUG, INFO, WARNING, ERROR
    "log_file": "grid_bot.log",       // Log file path
    "enable_market_data_stream": true, // Use real-time data
    "market_data_fallback": true,     // Enable fallback price provider
    "fallback_update_interval": 10,   // Fallback update interval
    "dry_run": false,                 // Dry run mode (no actual trading)
    "auto_restart": false,            // Auto-restart on errors
    "max_restart_attempts": 3         // Max restart attempts
  }
}
```

### Notifications (Optional)
```json
{
  "notifications": {
    "enabled": false,
    "email": {
      "enabled": false,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "your_email@gmail.com",
      "password": "your_app_password",
      "to_address": "alerts@example.com"
    },
    "webhook": {
      "enabled": false,
      "url": "https://hooks.slack.com/services/...",
      "events": ["trade", "error", "stop"]
    }
  }
}
```

## Parameter Guidelines

### Conservative Setup (Low Risk)
- Grid Levels: 5-8
- Grid Spacing: 3-5%
- Initial Quantity: 5-8%
- Wallet Exposure: 15-25%
- Max Position: 2000-3000 shares

### Moderate Setup (Balanced)
- Grid Levels: 8-12
- Grid Spacing: 2-3%
- Initial Quantity: 8-12%
- Wallet Exposure: 25-40%
- Max Position: 5000-7000 shares

### Aggressive Setup (High Risk)
- Grid Levels: 12-20
- Grid Spacing: 1-2%
- Initial Quantity: 10-15%
- Wallet Exposure: 40-60%
- Max Position: 8000-15000 shares

## Environment Variables

You can override configuration using environment variables:

```bash
export DNSE_USERNAME="your_username"
export DNSE_PASSWORD="your_password"
export GRID_SYMBOL="VIC"
export GRID_LEVELS="10"
export GRID_SPACING="0.025"
export DRY_RUN="true"
export LOG_LEVEL="DEBUG"
```

## Command Line Usage

```bash
# Create default config
python run_grid_bot.py --create-config

# Test with dry run
python run_grid_bot.py --dry-run

# Custom symbol and levels
python run_grid_bot.py --symbol VIC --levels 10 --spacing 0.025

# Live trading
python run_grid_bot.py
```

## Example Complete Configuration

```json
{
  "api": {
    "username": "trader@example.com",
    "password": "secure_password_123",
    "base_url": "https://api.dnse.com.vn",
    "mqtt_host": "datafeed-lts-krx.dnse.com.vn",
    "mqtt_port": 443,
    "timeout": 15,
    "retry_attempts": 3
  },
  "strategy": {
    "symbol": "HPG",
    "account_no": "",
    "loan_package_id": null,
    "grid_mode": "recursive",
    "grid_levels": 10,
    "grid_spacing_pct": 0.025,
    "grid_span_pct": 0.20,
    "initial_qty_pct": 0.10,
    "ddown_factor": 1.6,
    "max_position_size": 8000,
    "min_markup_pct": 0.008,
    "markup_range_pct": 0.020,
    "wallet_exposure_limit_pct": 0.35,
    "max_drawdown_pct": 0.10,
    "stop_loss_pct": 0.15,
    "ema_span_0": 12,
    "ema_span_1": 26,
    "use_ema_smoothing": true,
    "price_precision": 0,
    "min_order_value": 100000
  },
  "risk": {
    "max_daily_loss": 2000000,
    "max_open_orders": 25,
    "position_size_limit": 0.6,
    "emergency_stop_enabled": true,
    "emergency_stop_loss_pct": 0.20
  },
  "operational": {
    "monitoring_interval": 3,
    "log_level": "INFO",
    "log_file": "grid_bot.log",
    "enable_market_data_stream": true,
    "market_data_fallback": true,
    "fallback_update_interval": 5,
    "dry_run": false,
    "auto_restart": false,
    "max_restart_attempts": 3
  },
  "notifications": {
    "enabled": false
  }
}
```

## Important Notes

1. **Start with dry run mode** to test your configuration
2. **Use conservative settings** when starting out
3. **Monitor the bot closely** especially during the first few hours
4. **Set appropriate stop losses** to limit downside risk
5. **Test thoroughly** in paper trading before going live

## Support

For issues or questions:
1. Check the logs in `grid_bot.log`
2. Run with `--log-level DEBUG` for detailed information
3. Test with `--dry-run` to isolate configuration issues
4. Refer to the GRID_TRADING_README.md for troubleshooting
