#!/usr/bin/env python3
"""
Test script for the DNSE Grid Trading Bot

This script performs basic validation of the grid trading implementation
without requiring actual DNSE API credentials.
"""

import sys
from pathlib import Path
from decimal import Decimal

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_grid_config():
    """Test GridConfig validation"""
    print("Testing GridConfig...")
    
    from strategies.grid_base import GridConfig
    
    # Test valid configuration
    config = GridConfig(
        symbol="HPG",
        account_no="test_account",
        grid_levels=8,
        grid_spacing_pct=Decimal('0.02'),
        initial_qty_pct=Decimal('0.08'),
        max_position_size=5000,
        wallet_exposure_limit_pct=Decimal('0.25')
    )
    
    errors = config.validate()
    assert len(errors) == 0, f"Valid config should have no errors: {errors}"
    print("✓ Valid configuration passes validation")
    
    # Test invalid configuration
    invalid_config = GridConfig(
        symbol="",
        account_no="test_account",
        grid_levels=1,  # Too few levels
        grid_spacing_pct=Decimal('0'),  # Invalid spacing
        initial_qty_pct=Decimal('1.5'),  # > 100%
        max_position_size=0,  # Invalid size
        wallet_exposure_limit_pct=Decimal('2.0')  # > 100%
    )
    
    errors = invalid_config.validate()
    assert len(errors) > 0, "Invalid config should have errors"
    print(f"✓ Invalid configuration caught {len(errors)} errors")

def test_price_utils():
    """Test price utility functions"""
    print("Testing PriceUtils...")
    
    from strategies.grid_base import PriceUtils
    
    # Test price rounding
    price = Decimal('26750.7')
    rounded = PriceUtils.round_price(price, 0)
    assert rounded == Decimal('26751'), f"Expected 26751, got {rounded}"
    print("✓ Price rounding works correctly")
    
    # Test grid price calculation
    center_price = Decimal('26000')
    grid_levels = 5
    spacing = Decimal('0.02')
    
    prices = PriceUtils.calculate_grid_prices(center_price, grid_levels, spacing, "symmetric")
    assert len(prices) == grid_levels, f"Expected {grid_levels} prices, got {len(prices)}"
    assert all(p > 0 for p in prices), "All prices should be positive"
    print(f"✓ Grid prices calculated: {[float(p) for p in prices[:3]]}")
    
    # Test quantity calculation
    capital = Decimal('10000000')  # 10M VND
    price = Decimal('26000')
    qty_pct = Decimal('0.1')
    min_order = Decimal('100000')
    
    quantity = PriceUtils.calculate_quantity_for_price(capital, price, qty_pct, min_order)
    expected = int((capital * qty_pct) / price)
    assert quantity == expected, f"Expected {expected}, got {quantity}"
    print(f"✓ Quantity calculation: {quantity} shares")

def test_grid_position():
    """Test position tracking"""
    print("Testing GridPosition...")
    
    from strategies.grid_base import GridPosition
    
    position = GridPosition(symbol="HPG")
    
    # Test buy order
    position.update_position(100, Decimal('26000'), 'BUY')
    assert position.total_quantity == 100
    assert position.average_price == Decimal('26000')
    print(f"✓ After buy: {position.total_quantity} @ {position.average_price}")
    
    # Test another buy (DCA)
    position.update_position(200, Decimal('25000'), 'BUY')
    expected_avg = (Decimal('26000') * 100 + Decimal('25000') * 200) / 300
    assert position.total_quantity == 300
    assert abs(position.average_price - expected_avg) < Decimal('0.01')
    print(f"✓ After DCA: {position.total_quantity} @ {position.average_price}")
    
    # Test sell order
    position.update_position(100, Decimal('27000'), 'SELL')
    assert position.total_quantity == 200
    assert position.realized_pnl > 0  # Should have profit
    print(f"✓ After sell: {position.total_quantity} shares, realized P&L: {position.realized_pnl}")

def test_risk_manager():
    """Test risk management"""
    print("Testing RiskManager...")
    
    from strategies.grid_base import GridConfig, RiskManager
    
    config = GridConfig(
        symbol="HPG",
        account_no="test",
        wallet_exposure_limit_pct=Decimal('0.3'),
        max_position_size=1000,
        stop_loss_pct=Decimal('0.1')
    )
    
    risk_manager = RiskManager(config)
    
    # Test exposure check
    position_value = Decimal('2000000')  # 2M VND
    wallet_value = Decimal('10000000')   # 10M VND
    assert risk_manager.check_wallet_exposure(position_value, wallet_value)
    print("✓ Exposure within limits")
    
    # Test position size check
    assert risk_manager.check_max_position_size(500, 400)  # 900 total < 1000 max
    assert not risk_manager.check_max_position_size(800, 400)  # 1200 total > 1000 max
    print("✓ Position size checks work")
    
    # Test stop loss calculation
    avg_price = Decimal('26000')
    stop_price = risk_manager.calculate_stop_loss_price(avg_price)
    expected_stop = avg_price * Decimal('0.9')  # 10% stop loss
    assert stop_price == expected_stop
    print(f"✓ Stop loss: {stop_price} (10% below {avg_price})")

def test_config_manager():
    """Test configuration management"""
    print("Testing ConfigManager...")
    
    from strategies.config_manager import ConfigManager
    import tempfile
    import os
    
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        config_manager = ConfigManager(config_file)
        
        # Test creating default config
        config_manager.create_default_config()
        assert Path(config_file).exists()
        print("✓ Default configuration created")
        
        # Set dry run mode to skip credential validation
        import os
        os.environ["DRY_RUN"] = "true"
        
        # Test loading config
        success = config_manager.load_config()
        assert success, "Should load config successfully"
        print("✓ Configuration loaded")
        
        # Test getting values
        symbol = config_manager.get_value('strategy', 'symbol')
        assert symbol == 'HPG', f"Expected HPG, got {symbol}"
        print(f"✓ Configuration value retrieved: {symbol}")
        
        # Test validation
        errors = config_manager.get_validation_errors()
        print(f"✓ Validation completed with {len(errors)} errors")
        
    finally:
        # Cleanup
        if os.path.exists(config_file):
            os.unlink(config_file)

def main():
    """Run all tests"""
    print("🧪 DNSE Grid Trading Bot - Test Suite")
    print("=" * 50)
    
    try:
        test_grid_config()
        print()
        
        test_price_utils()
        print()
        
        test_grid_position()
        print()
        
        test_risk_manager()
        print()
        
        test_config_manager()
        print()
        
        print("🎉 All tests passed!")
        print("\n✅ The grid trading implementation appears to be working correctly.")
        print("📝 Next steps:")
        print("   1. Create configuration: python run_grid_bot.py --create-config")
        print("   2. Edit configuration with your DNSE credentials")
        print("   3. Test with dry run: python run_grid_bot.py --dry-run")
        print("   4. Run live trading: python run_grid_bot.py")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
