import requests

def send_telegram_alert(trade_result, bot_token, chat_id):
    message = (
        f"Trade Alert!\n"
        f"Symbol: {trade_result['symbol']}\n"
        f"Side: {trade_result['side']}\n"
        f"Market: {trade_result['market']}\n"
        f"Confidence: {trade_result['confidence']}\n"
        f"Reason: {trade_result['reason']}\n"
        f"Status: {trade_result['status']}"
    )
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Telegram alert error: {e}") 