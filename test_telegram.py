import os
from utils import load_config
import requests

def test_telegram():
    config = load_config()
    bot_token = config.get('TELEGRAM_BOT_TOKEN')
    chat_id = config.get('TELEGRAM_CHAT_ID')
    if not bot_token or not chat_id:
        print('❌ Telegram bot token or chat ID not set in .env')
        return
    message = '✅ Telegram test: Your trading bot can send messages!'
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {'chat_id': chat_id, 'text': message}
    try:
        resp = requests.post(url, data=data, timeout=10)
        resp.raise_for_status()
        print('✅ Telegram message sent successfully!')
    except Exception as e:
        print(f'❌ Telegram test failed: {e}')

if __name__ == '__main__':
    test_telegram() 