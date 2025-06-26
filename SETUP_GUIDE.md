# Quick Setup Guide

## 🚀 Get Your Trading Bot Running in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Create Configuration File
1. Copy `config_template.txt` to `.env`
2. Fill in your API keys (see API setup below)

### Step 3: Test Everything Works
```bash
python test_bot.py
```

### Step 4: Run the Bot
```bash
python main.py
```

## 🔑 API Setup Quick Reference

### Gemini 2.0 Flash API (Free)
1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key to your `.env` file

### Binance API
1. Visit: https://www.binance.com/en/my/settings/api-management
2. Create new API key
3. Enable "Spot & Margin Trading" and "Futures"
4. Copy API key and secret to `.env`

### Telegram Bot (Optional)
1. Message @BotFather on Telegram
2. Send `/newbot` and follow instructions
3. Get your chat ID: message your bot, then visit:
   `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`

## 📝 Example .env File
```
GEMINI_API_KEY=AIzaSyC...
BINANCE_API_KEY=your_binance_key_here
BINANCE_API_SECRET=your_binance_secret_here
TELEGRAM_BOT_TOKEN=1234567890:ABC...
TELEGRAM_CHAT_ID=123456789
TRADE_QUANTITY=0.001
```

## ⚠️ Important Notes
- Start with small trade quantities (0.001)
- The bot runs every hour by default
- Only trades with >70% confidence
- HOLD actions don't execute trades
- Test thoroughly before using real money

## 🆘 Troubleshooting
- **"Missing configuration"**: Check your `.env` file
- **"API errors"**: Verify your API keys are correct
- **"No market data"**: Check your internet connection
- **"Trade failed"**: Ensure Binance API has trading permissions

## 📞 Need Help?
1. Run `python test_bot.py` to diagnose issues
2. Check the logs in `trade_log.jsonl`
3. Verify all API keys are correctly set 