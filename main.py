import time
import sys
from datetime import datetime
from coingecko_api import fetch_top_coins
from gemini_strategy import get_trade_signal
from binance_api import execute_trade
from notifier import send_telegram_alert
from logger import log_trade
from utils import load_config

SLEEP_INTERVAL = 600  # 10 minutes

def validate_config(config):
    """Validate that all required configuration is present"""
    required_keys = ['GEMINI_API_KEY', 'BINANCE_API_KEY', 'BINANCE_API_SECRET', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']
    missing_keys = [key for key in required_keys if not config.get(key)]
    
    if missing_keys:
        print(f"❌ Missing required configuration: {missing_keys}")
        print("Please check config_template.txt for setup instructions")
        return False
    
    print("✅ Configuration validated successfully")
    return True

def main():
    print("🤖 Starting Crypto Trading Bot...")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load and validate configuration
    config = load_config()
    if not validate_config(config):
        print("❌ Configuration validation failed. Exiting.")
        sys.exit(1)
    
    iteration = 0
    while True:
        iteration += 1
        print(f"\n🔄 Trading iteration #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 1. Fetch market data
            print("📊 Fetching market data...")
            market_data = fetch_top_coins()
            if not market_data:
                print("⚠️  No market data received, skipping iteration")
                time.sleep(SLEEP_INTERVAL)
                continue
            
            print(f"✅ Fetched data for {len(market_data)} coins")
            
            # 2. Get trade signal from Gemini
            print("🧠 Getting AI trade signal...")
            signal = get_trade_signal(market_data, config['GEMINI_API_KEY'])
            print(f"📈 Signal: {signal['action']} {signal['symbol']} on {signal['market']} (confidence: {signal['confidence']}%)")
            
            # 3. Execute trade on Binance
            print("💱 Executing trade...")
            trade_result = execute_trade(signal, config)
            print(f"📋 Trade status: {trade_result['status']}")
            
            # 4. Log trade
            log_trade(trade_result)
            print("📝 Trade logged")
            
            # 5. Send Telegram alert
            if config.get('TELEGRAM_BOT_TOKEN') and config.get('TELEGRAM_CHAT_ID'):
                print("📱 Sending Telegram alert...")
                send_telegram_alert(trade_result, config['TELEGRAM_BOT_TOKEN'], config['TELEGRAM_CHAT_ID'])
                print("✅ Alert sent")
            else:
                print("⚠️  Telegram not configured, skipping alert")
            
            print(f"✅ Iteration #{iteration} completed successfully")
            
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user")
            break
        except Exception as e:
            print(f"❌ Error in iteration #{iteration}: {e}")
            print("🔄 Continuing to next iteration...")
        
        print(f"⏳ Waiting {SLEEP_INTERVAL} seconds until next iteration...")
        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main() 