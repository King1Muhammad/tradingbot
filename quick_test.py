#!/usr/bin/env python3
"""
Quick test to verify the bot runs without format string errors
"""

import sys
from datetime import datetime
from coingecko_api import fetch_top_coins
from gemini_strategy import get_trade_signal
from binance_api import execute_trade
from utils import load_config

def quick_test():
    """Run a quick test of the main bot components"""
    print("🧪 Quick Bot Test")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Load config
        config = load_config()
        print("✅ Config loaded")
        
        # Fetch market data
        market_data = fetch_top_coins()
        print(f"✅ Market data: {len(market_data)} coins")
        
        # Get AI signal
        signal = get_trade_signal(market_data, config.get('GEMINI_API_KEY'))
        print(f"✅ AI signal: {signal['action']} {signal['symbol']} (confidence: {signal['confidence']}%)")
        
        # Execute trade (should be HOLD, so no actual trade)
        trade_result = execute_trade(signal, config)
        print(f"✅ Trade result: {trade_result['status']}")
        print(f"✅ Timestamp: {trade_result['timestamp']}")
        
        print("\n🎉 All tests passed! No format string errors.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1) 