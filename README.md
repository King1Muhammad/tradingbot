# Modular Python Crypto Trading Bot

A modular, free-API-based crypto trading bot that fetches top coin data from CoinGecko, uses Gemini 2.0 Flash AI for trade decisions, executes trades on Binance (Spot & Futures), logs all activity, and sends Telegram alerts.

## Features
- Fetches real-time top coin data (price, market cap, volume) from CoinGecko
- Uses Gemini 2.0 Flash API for AI-powered trade signals
- Executes Spot and Futures trades on Binance (market orders, 1x leverage)
- Logs all trades locally (JSONL)
- Sends Telegram alerts for every trade
- Runs every hour, 24/7
- Modular, extensible codebase
- Comprehensive error handling and validation
- Test suite for component verification

## Prerequisites
- Python 3.7+
- Binance API keys (Spot & Futures enabled)
- Gemini 2.0 Flash API key
- Telegram bot token and chat ID

## Installation

1. **Clone or download the project files**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up configuration:**
   - Copy `config_template.txt` to `.env`
   - Fill in your API keys and settings:
   ```
   # Gemini 2.0 Flash API Key
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # Binance API Keys
   BINANCE_API_KEY=your_binance_api_key_here
   BINANCE_API_SECRET=your_binance_api_secret_here
   
   # Telegram Bot
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   TELEGRAM_CHAT_ID=your_telegram_chat_id_here
   
   # Trading Configuration
   TRADE_QUANTITY=0.001
   ```

4. **Test the setup:**
   ```bash
   python test_bot.py
   ```

## Usage

**Run the bot:**
```bash
python main.py
```

The bot will:
1. Validate your configuration
2. Run continuously, executing the trading loop every hour
3. Display detailed logs of each step
4. Handle errors gracefully and continue running

**Stop the bot:**
Press `Ctrl+C` to stop the bot safely.

## File Descriptions
- `main.py`: Orchestrates the trading loop with enhanced error handling and logging
- `coingecko_api.py`: Fetches top coin data from CoinGecko
- `gemini_strategy.py`: Uses Gemini 2.0 Flash API for trade decisions
- `binance_api.py`: Executes Spot/Futures trades on Binance with proper validation
- `notifier.py`: Sends Telegram alerts for every trade
- `logger.py`: Logs all trade activity to `trade_log.jsonl`
- `utils.py`: Loads environment variables using python-dotenv
- `test_bot.py`: Test suite to verify all components work correctly
- `config_template.txt`: Template for creating your `.env` file
- `requirements.txt`: Python dependencies with version specifications

## API Setup Instructions

### Gemini 2.0 Flash API
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

### Binance API
1. Go to [Binance API Management](https://www.binance.com/en/my/settings/api-management)
2. Create a new API key with Spot & Futures trading permissions
3. Add both API key and secret to your `.env` file

### Telegram Bot
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot and get the token
3. Message your bot to start a conversation
4. Get your chat ID: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
5. Add both token and chat ID to your `.env` file

## Recent Improvements
- ✅ Fixed HOLD action handling (no longer tries to execute HOLD orders)
- ✅ Enhanced error handling and validation throughout
- ✅ Updated to use Gemini 2.0 Flash API for better performance
- ✅ Improved configuration management with python-dotenv
- ✅ Added comprehensive test suite
- ✅ Better logging and user feedback
- ✅ Fixed API integration issues
- ✅ Added proper dependency management
- ✅ Fixed timestamp formatting compatibility issues

## Notes
- All API keys and secrets are loaded securely from `.env`
- Trade logs are written to `trade_log.jsonl` (one JSON object per line)
- Only free APIs and tools are used
- Error handling is implemented throughout
- The bot is conservative and only trades with high confidence (>70%)
- HOLD actions are properly handled (no trade execution)

## Extending
- Add new strategies by editing `gemini_strategy.py`
- Add more exchanges or notification channels by creating new modules
- Modify the trading interval in `main.py` (SLEEP_INTERVAL)
- Adjust confidence thresholds in `gemini_strategy.py`

---
**Disclaimer:** This bot is for educational purposes only. Use at your own risk. Crypto trading involves significant risk. Always test with small amounts first. 