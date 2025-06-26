import requests

def fetch_top_coins(limit=5):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': limit,
        'page': 1,
        'sparkline': False
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [
            {
                'symbol': coin['symbol'].upper(),
                'id': coin['id'],
                'price': coin['current_price'],
                'market_cap': coin['market_cap'],
                'volume': coin['total_volume']
            } for coin in data
        ]
    except Exception as e:
        print(f"CoinGecko API error: {e}")
        return [] 