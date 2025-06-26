import os
from dotenv import load_dotenv

def load_config(env_file='.env'):
    """Load configuration from .env file and environment variables"""
    # Load .env file if it exists
    if os.path.exists(env_file):
        load_dotenv(env_file)
    
    config = {
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'BINANCE_API_KEY': os.getenv('BINANCE_API_KEY'),
        'BINANCE_API_SECRET': os.getenv('BINANCE_API_SECRET'),
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID'),
        'TRADE_QUANTITY': float(os.getenv('TRADE_QUANTITY', '0.001')),
        # Advanced futures risk management
        'FUTURES_LEVERAGE': int(os.getenv('FUTURES_LEVERAGE', '1')),
        'FUTURES_MAX_DAILY_LOSS': float(os.getenv('FUTURES_MAX_DAILY_LOSS', '0')),
        'FUTURES_STOP_LOSS_PERCENT': float(os.getenv('FUTURES_STOP_LOSS_PERCENT', '0')),
        'FUTURES_TAKE_PROFIT_PERCENT': float(os.getenv('FUTURES_TAKE_PROFIT_PERCENT', '0')),
        'FUTURES_USE_BALANCE_PERCENT': float(os.getenv('FUTURES_USE_BALANCE_PERCENT', '0')),
        'FUTURES_MAX_TRADES_PER_DAY': int(os.getenv('FUTURES_MAX_TRADES_PER_DAY', '0')),
        'PAPER_TRADING': int(os.getenv('PAPER_TRADING', '0')),
    }
    
    # Validate required config
    missing_keys = [key for key, value in config.items() if value is None and key != 'TRADE_QUANTITY']
    if missing_keys:
        print(f"Warning: Missing required environment variables: {missing_keys}")
    
    return config 