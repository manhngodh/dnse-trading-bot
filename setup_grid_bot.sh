#!/bin/bash

# DNSE Grid Trading Bot - Quick Setup Script
# This script helps you get started with the grid trading bot

set -e

echo "🤖 DNSE Grid Trading Bot - Quick Setup"
echo "======================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if we're in the correct directory
if [ ! -f "run_grid_bot.py" ]; then
    echo "❌ Please run this script from the dnse-trading-bot directory"
    exit 1
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
if [ -f "backend/requirements.txt" ]; then
    pip3 install -r backend/requirements.txt
    echo "✅ Dependencies installed"
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# Create configuration
echo ""
echo "⚙️  Setting up configuration..."
if [ ! -f "grid_bot_config.json" ]; then
    python3 run_grid_bot.py --create-config
    echo "✅ Default configuration created"
else
    echo "⚠️  Configuration file already exists"
fi

# Run tests
echo ""
echo "🧪 Running tests..."
if python3 test_grid_bot.py; then
    echo "✅ All tests passed"
else
    echo "❌ Tests failed. Please check the installation."
    exit 1
fi

# Provide setup instructions
echo ""
echo "🎉 Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit grid_bot_config.json with your DNSE credentials:"
echo "   - Set your username and password in the 'api' section"
echo "   - Adjust strategy parameters as needed"
echo ""
echo "2. Test the bot in dry-run mode:"
echo "   python3 run_grid_bot.py --dry-run"
echo ""
echo "3. When ready, run live trading:"
echo "   python3 run_grid_bot.py"
echo ""
echo "📚 Documentation:"
echo "   - Configuration examples: CONFIG_EXAMPLES.md"
echo "   - Full documentation: GRID_TRADING_README.md"
echo ""
echo "⚠️  Important reminders:"
echo "   - Always test with --dry-run first"
echo "   - Start with conservative settings"
echo "   - Monitor the bot closely when live"
echo "   - Set appropriate risk limits"
echo ""
echo "🚀 Happy trading!"
