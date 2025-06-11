#!/usr/bin/env python3
"""
DNSE Grid Trading Bot Launcher

This script provides a simple interface to launch the grid trading bot
with various options and configurations.
"""

import argparse
import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def main():
    parser = argparse.ArgumentParser(
        description="DNSE Grid Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_grid_bot.py                           # Run with default config
  python run_grid_bot.py --config my_config.json   # Run with custom config
  python run_grid_bot.py --dry-run                 # Run in dry-run mode
  python run_grid_bot.py --symbol VIC --levels 10  # Override symbol and grid levels
        """
    )
    
    parser.add_argument(
        "--config", "-c",
        default="grid_bot_config.json",
        help="Configuration file path (default: grid_bot_config.json)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (no actual trading)"
    )
    
    parser.add_argument(
        "--symbol", "-s",
        help="Trading symbol (overrides config)"
    )
    
    parser.add_argument(
        "--levels",
        type=int,
        help="Number of grid levels (overrides config)"
    )
    
    parser.add_argument(
        "--spacing",
        type=float,
        help="Grid spacing percentage (e.g., 0.02 for 2%)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    
    parser.add_argument(
        "--create-config",
        action="store_true",
        help="Create a default configuration file and exit"
    )
    
    args = parser.parse_args()
    
    # Set environment variables based on arguments
    if args.dry_run:
        os.environ["DRY_RUN"] = "true"
    
    if args.symbol:
        os.environ["GRID_SYMBOL"] = args.symbol
    
    if args.levels:
        os.environ["GRID_LEVELS"] = str(args.levels)
    
    if args.spacing:
        os.environ["GRID_SPACING"] = str(args.spacing)
    
    os.environ["LOG_LEVEL"] = args.log_level
    
    # Handle create config option
    if args.create_config:
        from strategies.config_manager import ConfigManager
        config_manager = ConfigManager(args.config)
        config_manager.create_default_config()
        print(f"Default configuration created at {args.config}")
        print("Please edit the configuration file with your DNSE credentials and preferences.")
        return
    
    # Import and run the bot
    try:
        from grid_trading_bot import GridTradingBot
        import asyncio
        
        print("=== DNSE Grid Trading Bot ===")
        print(f"Configuration file: {args.config}")
        print(f"Log level: {args.log_level}")
        if args.dry_run:
            print("⚠️  DRY RUN MODE - No actual trading will occur")
        print("=" * 40)
        
        # Create and run bot
        bot = GridTradingBot(args.config)
        asyncio.run(bot.initialize_and_run())
        
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the correct directory and dependencies are installed.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
