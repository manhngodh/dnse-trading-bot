# DNSE Grid Trading Bot

A sophisticated Python-based automated grid trading bot designed for the DNSE LightSpeed API. This implementation follows the architectural principles outlined in the project blueprint and draws inspiration from established grid trading systems like Passivbot.

## 🎯 Features

### Core Grid Trading Strategy
- **Recursive Grid Mode**: Dynamic grid calculation where each subsequent level is based on the previous fill
- **Market Making**: Exclusively uses limit orders for better fees and liquidity provision
- **DCA (Dollar Cost Averaging)**: Intelligent position sizing with configurable multipliers
- **Risk Management**: Comprehensive risk controls with exposure limits and stop losses

### Advanced Capabilities
- **Real-time Market Data**: MQTT-based live price feeds with fallback mechanisms
- **EMA Smoothing**: Exponential moving averages for entry timing optimization
- **Configurable Parameters**: Extensive customization options for different market conditions
- **Performance Tracking**: Detailed trade history and P&L monitoring
- **Graceful Shutdown**: Safe order cancellation and position management

## 📁 Project Structure

```
backend/
├── strategies/
│   ├── __init__.py
│   ├── grid_base.py          # Core grid trading classes and utilities
│   ├── recursive_grid.py     # Recursive grid strategy implementation
│   ├── market_data.py        # Real-time market data handling
│   └── config_manager.py     # Configuration management
├── cli/
│   └── dnse_client_v2.py     # DNSE API client
├── grid_trading_bot.py       # Main bot orchestrator
└── requirements.txt          # Python dependencies
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
cd dnse-trading-bot

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Configuration

Create a configuration file:

```bash
python run_grid_bot.py --create-config
```

Edit `grid_bot_config.json` with your settings:

```json
{
  "api": {
    "username": "your_dnse_username",
    "password": "your_dnse_password"
  },
  "strategy": {
    "symbol": "HPG",
    "grid_levels": 8,
    "grid_spacing_pct": 0.02,
    "initial_qty_pct": 0.08,
    "max_position_size": 5000,
    "wallet_exposure_limit_pct": 0.25
  },
  "operational": {
    "dry_run": false
  }
}
```

### 3. Running the Bot

```bash
# Test run (no actual trading)
python run_grid_bot.py --dry-run

# Live trading
python run_grid_bot.py

# Custom parameters
python run_grid_bot.py --symbol VIC --levels 10 --spacing 0.025
```

## ⚙️ Configuration Guide

### Strategy Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `symbol` | Trading symbol | "HPG" | Any valid symbol |
| `grid_levels` | Number of grid levels | 8 | 2-20 |
| `grid_spacing_pct` | Spacing between levels | 0.02 (2%) | 0.005-0.1 |
| `initial_qty_pct` | Initial order size | 0.08 (8%) | 0.01-0.5 |
| `ddown_factor` | DCA multiplier | 1.5 | 1.0-3.0 |
| `max_position_size` | Maximum total position | 5000 | 100-50000 |
| `min_markup_pct` | Minimum take profit | 0.005 (0.5%) | 0.001-0.05 |
| `wallet_exposure_limit_pct` | Max portfolio exposure | 0.25 (25%) | 0.1-0.8 |

### Risk Management

| Parameter | Description | Default |
|-----------|-------------|---------|
| `max_drawdown_pct` | Maximum drawdown before stop | 0.08 (8%) |
| `stop_loss_pct` | Position stop loss | None (disabled) |
| `emergency_stop_loss_pct` | Portfolio emergency stop | 0.15 (15%) |

## 🔧 Advanced Usage

### Environment Variables

Override configuration with environment variables:

```bash
export DNSE_USERNAME="your_username"
export DNSE_PASSWORD="your_password"
export GRID_SYMBOL="VIC"
export GRID_LEVELS="10"
export DRY_RUN="true"
```

### Custom Strategy Development

Extend the base classes for custom strategies:

```python
from strategies.grid_base import GridConfig, GridPosition
from strategies.recursive_grid import RecursiveGridStrategy

class CustomGridStrategy(RecursiveGridStrategy):
    def _calculate_order_quantity(self, price, grid_index):
        # Custom quantity calculation
        return super()._calculate_order_quantity(price, grid_index)
```

## 📊 Strategy Logic

### Grid Placement Algorithm

1. **Initial Setup**: Place buy orders below current market price
2. **Fill Detection**: Monitor for order executions via API polling
3. **Position Update**: Calculate new average price and unrealized P&L
4. **Take Profit**: Place sell orders above average price with markup
5. **Grid Replacement**: Add new buy orders at deeper levels
6. **Risk Monitoring**: Continuously check exposure and drawdown limits

### Order Flow Example

```
Current Price: 26,000 VND
Grid Spacing: 2%
Initial Quantity: 100 shares

Grid Levels:
- Buy 100 @ 25,480 (level 1)
- Buy 150 @ 24,970 (level 2) 
- Buy 225 @ 24,471 (level 3)
...

On Fill at 25,480:
- New avg price: 25,480
- Place sell 100 @ 25,607 (0.5% markup)
- Place new buy 338 @ 23,981 (level 4)
```

## 🛡️ Risk Management

### Built-in Protections

- **Position Size Limits**: Prevents over-exposure to single positions
- **Wallet Exposure**: Limits total capital at risk
- **Drawdown Monitoring**: Stops trading on excessive losses
- **Order Validation**: Checks all orders before placement
- **Emergency Stops**: Circuit breakers for extreme market moves

### Recommended Settings

**Conservative (Low Risk)**:
- Grid Levels: 5-8
- Spacing: 3-5%
- Exposure Limit: 15-25%

**Moderate (Balanced)**:
- Grid Levels: 8-12
- Spacing: 2-3%
- Exposure Limit: 25-40%

**Aggressive (High Risk)**:
- Grid Levels: 12-20
- Spacing: 1-2%
- Exposure Limit: 40-60%

## 🔍 Monitoring & Debugging

### Log Analysis

The bot provides comprehensive logging:

```bash
# View real-time logs
tail -f grid_bot.log

# Filter for specific events
grep "Order filled" grid_bot.log
grep "ERROR" grid_bot.log
```

### Performance Metrics

Monitor key metrics:
- Total P&L (realized + unrealized)
- Number of trades executed
- Win rate percentage
- Current position size
- Active grid orders

### Status API

```python
# Get current status
status = bot.strategy.get_status()
print(f"Position: {status['position']['quantity']}")
print(f"Unrealized P&L: {status['position']['unrealized_pnl']:,.0f}")
```

## ⚠️ Important Disclaimers

1. **Trading Risk**: This bot involves substantial risk of loss. Never risk more than you can afford to lose.

2. **Market Conditions**: Grid trading works best in ranging/choppy markets. Trending markets can lead to significant drawdowns.

3. **API Dependencies**: The bot relies on DNSE API availability and stability. Service interruptions may affect performance.

4. **Testing Required**: Always test thoroughly in a paper trading environment before live deployment.

5. **Monitoring Needed**: Automated trading still requires human oversight and intervention capabilities.

## 🆘 Troubleshooting

### Common Issues

**Connection Problems**:
```bash
# Check API credentials
export DNSE_USERNAME="your_username"
export DNSE_PASSWORD="your_password"

# Test connection
python -c "from cli.dnse_client_v2 import DNSEClient; client = DNSEClient('user', 'pass'); client.login()"
```

**Configuration Errors**:
```bash
# Validate configuration
python run_grid_bot.py --create-config
# Edit the generated file with correct values
```

**Market Data Issues**:
- Ensure MQTT ports (443) are not blocked
- Check network connectivity
- Verify market hours and symbol availability

### Emergency Shutdown

To safely stop the bot:

1. **Graceful**: `Ctrl+C` - Cancels all orders and closes positions
2. **Force**: `kill -TERM <pid>` - Immediate shutdown with cleanup
3. **Emergency**: Manually cancel orders via DNSE web interface

## 📈 Performance Optimization

### Parameter Tuning

1. **Backtest Different Configurations**: Test various grid spacings and levels
2. **Market Analysis**: Adjust parameters based on volatility and trend
3. **Capital Allocation**: Optimize position sizing for risk-adjusted returns

### System Optimization

- **VPS Deployment**: Use a reliable VPS for 24/7 operation
- **Redundancy**: Consider multiple bot instances with different parameters
- **Monitoring**: Set up alerts for position size and P&L thresholds

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request with clear description

## 📄 License

This project is for educational and research purposes. Users are responsible for compliance with all applicable laws and regulations.

---

**⚡ Ready to start grid trading? Create your configuration and run the bot!**

```bash
python run_grid_bot.py --create-config
# Edit grid_bot_config.json with your settings
python run_grid_bot.py --dry-run  # Test first!
```
