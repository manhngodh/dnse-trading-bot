# Main Grid Trading Bot Application
import asyncio
import logging
import os
import signal
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional

# Add parent directory to path to import DNSE client
sys.path.append(str(Path(__file__).parent.parent))

from cli.dnse_client_v2 import DNSEClient
from strategies.grid_base import GridConfig
from strategies.recursive_grid import RecursiveGridStrategy
from strategies.config_manager import ConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('grid_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GridTradingBot:
    """
    Main Trading Bot Application Orchestrator
    
    This class manages the lifecycle of the grid trading strategy,
    configuration loading, API client initialization, and overall bot execution.
    """
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config_manager: Optional[ConfigManager] = None
        self.grid_config: Optional[GridConfig] = None
        self.api_client: Optional[DNSEClient] = None
        self.strategy: Optional[RecursiveGridStrategy] = None
        self.is_running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
        self.is_running = False
    
    async def initialize(self) -> bool:
        """Initialize the bot with configuration and API client"""
        try:
            # Load configuration
            if not await self._load_configuration():
                return False
            
            # Initialize API client
            if not await self._initialize_api_client():
                return False
            
            # Create grid configuration
            if not self._create_grid_config():
                return False
            
            # Initialize strategy
            if not await self._initialize_strategy():
                return False
            
            logger.info("Grid Trading Bot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            return False
    
    async def _load_configuration(self) -> bool:
        """Load configuration using ConfigManager"""
        try:
            self.config_manager = ConfigManager(self.config_file)
            
            if not self.config_manager.load_config():
                logger.error("Failed to load configuration")
                return False
            
            # Print configuration summary
            self.config_manager.print_config_summary()
            
            logger.info(f"Configuration loaded from {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return False
    
    async def _initialize_api_client(self) -> bool:
        """Initialize and authenticate DNSE API client"""
        try:
            # Get credentials from config or environment
            api_config = self.config_manager.get_section('api')
            username = api_config.get('username') or os.getenv('DNSE_USERNAME')
            password = api_config.get('password') or os.getenv('DNSE_PASSWORD')
            
            if not username or not password:
                logger.error("DNSE credentials not found in config or environment variables")
                return False
            
            # Initialize client
            self.api_client = DNSEClient(username=username, password=password)
            
            # Login
            logger.info("Logging into DNSE...")
            self.api_client.login()
            
            # Get OTP from user (skip in dry run mode)
            operational_config = self.config_manager.get_section('operational')
            if not operational_config.get('dry_run', False):
                otp = input("Please enter the OTP sent to your email: ")
                self.api_client.verify_email_otp(otp)
            else:
                logger.info("Dry run mode - skipping OTP verification")
            
            # Get sub-accounts and update config if needed
            sub_accounts = self.api_client.get_sub_accounts()
            if sub_accounts and sub_accounts.get('accounts'):
                # Use first account if not specified in config
                current_account = self.config_manager.get_value('strategy', 'account_no')
                if not current_account:
                    account_no = sub_accounts['accounts'][0]['id']
                    self.config_manager.update_value('strategy', 'account_no', account_no)
                    logger.info(f"Using account: {account_no}")
            
            logger.info("DNSE API client initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize API client: {e}")
            return False
    
    def _create_grid_config(self) -> bool:
        """Create GridConfig from loaded configuration"""
        try:
            strategy_config = self.config_manager.get_section('strategy')
            
            self.grid_config = GridConfig(
                symbol=strategy_config.get('symbol', 'HPG'),
                account_no=strategy_config.get('account_no', ''),
                loan_package_id=strategy_config.get('loan_package_id'),
                grid_mode=strategy_config.get('grid_mode', 'recursive'),
                grid_levels=strategy_config.get('grid_levels', 8),
                grid_spacing_pct=Decimal(str(strategy_config.get('grid_spacing_pct', 0.02))),
                grid_span_pct=Decimal(str(strategy_config.get('grid_span_pct', 0.16))),
                initial_qty_pct=Decimal(str(strategy_config.get('initial_qty_pct', 0.08))),
                ddown_factor=Decimal(str(strategy_config.get('ddown_factor', 1.5))),
                max_position_size=strategy_config.get('max_position_size', 5000),
                min_markup_pct=Decimal(str(strategy_config.get('min_markup_pct', 0.005))),
                markup_range_pct=Decimal(str(strategy_config.get('markup_range_pct', 0.015))),
                wallet_exposure_limit_pct=Decimal(str(strategy_config.get('wallet_exposure_limit_pct', 0.25))),
                max_drawdown_pct=Decimal(str(strategy_config.get('max_drawdown_pct', 0.08))),
                stop_loss_pct=Decimal(str(strategy_config.get('stop_loss_pct'))) if strategy_config.get('stop_loss_pct') else None,
                ema_span_0=strategy_config.get('ema_span_0', 12),
                ema_span_1=strategy_config.get('ema_span_1', 26),
                use_ema_smoothing=strategy_config.get('use_ema_smoothing', True),
                price_precision=strategy_config.get('price_precision', 0),
                min_order_value=Decimal(str(strategy_config.get('min_order_value', 100000)))
            )
            
            # Validate configuration
            config_errors = self.grid_config.validate()
            if config_errors:
                logger.error(f"Invalid grid configuration: {', '.join(config_errors)}")
                return False
            
            logger.info(f"Grid configuration created for {self.grid_config.symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating grid configuration: {e}")
            return False
    
    async def _initialize_strategy(self) -> bool:
        """Initialize the grid trading strategy"""
        try:
            if self.grid_config.grid_mode == "recursive":
                self.strategy = RecursiveGridStrategy(self.grid_config, self.api_client)
            else:
                logger.error(f"Unsupported grid mode: {self.grid_config.grid_mode}")
                return False
            
            # Initialize strategy
            if not await self.strategy.initialize():
                logger.error("Failed to initialize strategy")
                return False
            
            logger.info(f"Strategy initialized: {self.grid_config.grid_mode} grid for {self.grid_config.symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing strategy: {e}")
            return False
    
    async def run(self) -> None:
        """Main bot execution loop"""
        if not self.strategy:
            logger.error("Strategy not initialized")
            return
        
        logger.info("Starting Grid Trading Bot...")
        self.is_running = True
        
        try:
            # Start the trading strategy
            strategy_task = asyncio.create_task(self.strategy.start_trading())
            
            # Start monitoring task
            monitor_task = asyncio.create_task(self._monitoring_loop())
            
            # Wait for either task to complete or for shutdown signal
            done, pending = await asyncio.wait(
                [strategy_task, monitor_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel pending tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
        except Exception as e:
            logger.error(f"Error in main execution loop: {e}")
        finally:
            await self._shutdown()
    
    async def _monitoring_loop(self) -> None:
        """Monitor bot status and log periodic updates"""
        operational_config = self.config_manager.get_section('operational')
        monitoring_interval = operational_config.get('monitoring_interval', 30)
        
        while self.is_running:
            try:
                if self.strategy:
                    status = self.strategy.get_status()
                    logger.info(f"Bot Status - "
                              f"Active: {status['is_active']}, "
                              f"Position: {status['position']['quantity']}, "
                              f"Grid Orders: {status['grid_orders']}, "
                              f"Total Trades: {status['total_trades']}")
                
                await asyncio.sleep(monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10)
    
    async def _shutdown(self) -> None:
        """Graceful shutdown procedure"""
        logger.info("Initiating graceful shutdown...")
        
        try:
            if self.strategy:
                await self.strategy.stop_trading()
            
            if self.api_client:
                self.api_client.disconnect_market_data()
            
            logger.info("Shutdown completed successfully")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    async def initialize_and_run(self) -> None:
        """Initialize and run the bot in one call"""
        if await self.initialize():
            await self.run()
        else:
            logger.error("Failed to initialize bot. Exiting.")
            sys.exit(1)

async def main():
    """Main entry point"""
    print("=== DNSE Grid Trading Bot ===")
    print("Starting initialization...")
    
    # Initialize bot
    bot = GridTradingBot("grid_bot_config.json")
    
    if await bot.initialize():
        print("Bot initialized successfully")
        print(f"Trading symbol: {bot.grid_config.symbol}")
        print(f"Grid levels: {bot.grid_config.grid_levels}")
        print(f"Grid spacing: {bot.grid_config.grid_spacing_pct:.1%}")
        print("Starting trading...")
        
        # Run the bot
        await bot.run()
    else:
        print("Failed to initialize bot. Please check the configuration and logs.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
