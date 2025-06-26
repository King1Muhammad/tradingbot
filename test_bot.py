#!/usr/bin/env python3
"""
Test script for the trading bot components
This script tests each module without executing actual trades
"""

import sys
from datetime import datetime
from coingecko_api import fetch_top_coins
from gemini_strategy import get_trade_signal
from utils import load_config

def test_market_data():
    """Test market data fetching"""
    print("🧪 Testing market data fetching...")
    try:
        data = fetch_top_coins()
        if data and len(data) > 0:
            print(f"✅ Successfully fetched data for {len(data)} coins")
            print(f"📊 Sample data: {data[0] if data else 'No data'}")
            return True
        else:
            print("❌ No market data received")
            return False
    except Exception as e:
        print(f"❌ Market data test failed: {e}")
        return False

def test_ai_strategy():
    """Test AI strategy (without API key)"""
    print("\n🧪 Testing AI strategy...")
    try:
        # Test with mock data
        mock_data = [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 50000,
                "market_cap": 1000000000000,
                "volume_24h": 50000000000,
                "price_change_24h": 2.5
            }
        ]
        
        # Test without API key (should return HOLD)
        signal = get_trade_signal(mock_data, None)
        print(f"✅ AI strategy test completed")
        print(f"📈 Signal: {signal}")
        
        # Validate signal structure
        required_fields = ['action', 'market', 'symbol', 'confidence', 'reason']
        missing_fields = [field for field in required_fields if field not in signal]
        
        if missing_fields:
            print(f"❌ Missing fields in signal: {missing_fields}")
            return False
        
        print("✅ Signal structure is valid")
        return True
        
    except Exception as e:
        print(f"❌ AI strategy test failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\n🧪 Testing configuration loading...")
    try:
        config = load_config()
        print(f"✅ Configuration loaded: {list(config.keys())}")
        
        # Check if .env file exists
        import os
        if os.path.exists('.env'):
            print("✅ .env file found")
        else:
            print("⚠️  .env file not found - using environment variables")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    print("🤖 Trading Bot Component Test")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_config),
        ("Market Data", test_market_data),
        ("AI Strategy", test_ai_strategy),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} test PASSED")
        else:
            print(f"❌ {test_name} test FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The bot components are working correctly.")
        print("\n📝 Next steps:")
        print("1. Create a .env file using config_template.txt as reference")
        print("2. Add your API keys to the .env file")
        print("3. Run: python main.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 