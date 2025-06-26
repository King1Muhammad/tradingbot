import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode
from datetime import datetime
import os
import json

def _get_binance_signature(query_string, secret):
    return hmac.new(secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

def _get_futures_usdt_balance(api_key, api_secret):
    url = "https://fapi.binance.com/fapi/v2/account"
    params = {'timestamp': int(time.time() * 1000)}
    query_string = urlencode(params)
    signature = _get_binance_signature(query_string, api_secret)
    params['signature'] = signature
    headers = {'X-MBX-APIKEY': api_key}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        for asset in data['assets']:
            if asset['asset'] == 'USDT':
                return float(asset['availableBalance'])
        return 0.0
    except Exception as e:
        print(f"Futures balance error: {e}")
        return 0.0

def _set_futures_leverage(symbol, leverage, api_key, api_secret):
    url = "https://fapi.binance.com/fapi/v1/leverage"
    params = {
        'symbol': symbol,
        'leverage': leverage,
        'timestamp': int(time.time() * 1000)
    }
    query_string = urlencode(params)
    signature = _get_binance_signature(query_string, api_secret)
    params['signature'] = signature
    headers = {'X-MBX-APIKEY': api_key}
    try:
        response = requests.post(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Set leverage error: {e}")
        return False

DAILY_STATS_FILE = 'futures_daily_stats.json'

def _load_daily_stats():
    today = datetime.utcnow().strftime('%Y-%m-%d')
    if os.path.exists(DAILY_STATS_FILE):
        try:
            with open(DAILY_STATS_FILE, 'r') as f:
                stats = json.load(f)
            if stats.get('date') == today:
                return stats
        except Exception:
            pass
    # New day or file missing/corrupt
    return {'date': today, 'trades': 0, 'realized_pnl': 0.0}

def _save_daily_stats(stats):
    with open(DAILY_STATS_FILE, 'w') as f:
        json.dump(stats, f)

def _update_daily_stats(pnl):
    stats = _load_daily_stats()
    stats['trades'] += 1
    stats['realized_pnl'] += pnl
    _save_daily_stats(stats)
    return stats

def _get_today_realized_pnl(api_key, api_secret):
    """Fetch today's realized PnL from Binance futures income history."""
    try:
        today = datetime.utcnow().strftime('%Y-%m-%d')
        start_time = int(datetime.strptime(today, '%Y-%m-%d').timestamp() * 1000)
        url = "https://fapi.binance.com/fapi/v1/income"
        params = {
            'incomeType': 'REALIZED_PNL',
            'startTime': start_time,
            'timestamp': int(time.time() * 1000)
        }
        query_string = urlencode(params)
        signature = _get_binance_signature(query_string, api_secret)
        params['signature'] = signature
        headers = {'X-MBX-APIKEY': api_key}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        total_pnl = sum(float(item['income']) for item in data if item['asset'] == 'USDT')
        return total_pnl
    except Exception as e:
        print(f"Realized PnL fetch error: {e}")
        return 0.0

def execute_trade(signal, config):
    """Execute trade based on signal, return trade result"""
    # Validate signal
    if not signal or 'action' not in signal:
        return {
            'symbol': 'UNKNOWN',
            'side': 'ERROR',
            'market': 'UNKNOWN',
            'confidence': 0,
            'reason': 'Invalid signal received',
            'status': 'FAILED',
            'response': None,
            'timestamp': datetime.now().isoformat()
        }
    
    # Handle HOLD action - no trade execution
    if signal['action'] == 'HOLD':
        return {
            'symbol': signal.get('symbol', 'UNKNOWN'),
            'side': 'HOLD',
            'market': signal.get('market', 'UNKNOWN'),
            'confidence': signal.get('confidence', 0),
            'reason': signal.get('reason', 'No trade executed (action was HOLD)'),
            'status': 'SKIPPED',
            'response': None,
            'timestamp': datetime.now().isoformat()
        }
    
    # Validate required fields for actual trades
    if signal['action'] not in ['BUY', 'SELL']:
        return {
            'symbol': signal.get('symbol', 'UNKNOWN'),
            'side': signal['action'],
            'market': signal.get('market', 'UNKNOWN'),
            'confidence': signal.get('confidence', 0),
            'reason': f"Invalid action: {signal['action']}",
            'status': 'FAILED',
            'response': None,
            'timestamp': datetime.now().isoformat()
        }
    
    # Check if API keys are available
    if not config.get('BINANCE_API_KEY') or not config.get('BINANCE_API_SECRET'):
        return {
            'symbol': signal.get('symbol', 'UNKNOWN'),
            'side': signal['action'],
            'market': signal.get('market', 'UNKNOWN'),
            'confidence': signal.get('confidence', 0),
            'reason': 'Binance API keys not configured',
            'status': 'FAILED',
            'response': None,
            'timestamp': datetime.now().isoformat()
        }
    
    api_key = config['BINANCE_API_KEY']
    api_secret = config['BINANCE_API_SECRET']
    base_url = 'https://api.binance.com' if signal.get('market', 'SPOT') == 'SPOT' else 'https://fapi.binance.com'
    endpoint = '/api/v3/order' if signal.get('market', 'SPOT') == 'SPOT' else '/fapi/v1/order'
    symbol = signal.get('symbol', 'BTCUSDT')
    side = signal['action']
    quantity = config.get('TRADE_QUANTITY', 0.001)
    
    paper_trading = config.get('PAPER_TRADING', 0) == 1
    
    # --- Advanced futures risk management ---
    if signal.get('market') == 'FUTURES':
        # Enforce max trades per day and max daily loss
        stats = _load_daily_stats()
        max_trades = config.get('FUTURES_MAX_TRADES_PER_DAY', 0)
        max_loss = config.get('FUTURES_MAX_DAILY_LOSS', 0)
        if (max_trades > 0 and stats['trades'] >= max_trades):
            return {
                'symbol': signal.get('symbol', 'UNKNOWN'),
                'side': signal['action'],
                'market': signal.get('market', 'FUTURES'),
                'confidence': signal.get('confidence', 0),
                'reason': f"Max trades per day ({max_trades}) reached.",
                'status': 'SKIPPED',
                'response': None,
                'timestamp': datetime.now().isoformat()
            }
        if (max_loss > 0 and stats['realized_pnl'] <= -abs(max_loss)):
            return {
                'symbol': signal.get('symbol', 'UNKNOWN'),
                'side': signal['action'],
                'market': signal.get('market', 'FUTURES'),
                'confidence': signal.get('confidence', 0),
                'reason': f"Max daily loss (${max_loss}) reached.",
                'status': 'SKIPPED',
                'response': None,
                'timestamp': datetime.now().isoformat()
            }
        # 1. Set leverage
        leverage = config.get('FUTURES_LEVERAGE', 1)
        _set_futures_leverage(symbol, leverage, api_key, api_secret)
        # 2. Calculate position size as 3% of available USDT balance
        use_balance_percent = config.get('FUTURES_USE_BALANCE_PERCENT', 0)
        if use_balance_percent > 0:
            usdt_balance = _get_futures_usdt_balance(api_key, api_secret)
            if usdt_balance > 0:
                # Get price for symbol (e.g., BTCUSDT)
                price_url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
                try:
                    price_resp = requests.get(price_url, timeout=10)
                    price_resp.raise_for_status()
                    price = float(price_resp.json()['price'])
                    notional = usdt_balance * use_balance_percent / 100
                    quantity = round(notional / price, 6)  # 6 decimals for futures
                except Exception as e:
                    print(f"Price fetch error: {e}")
        if paper_trading:
            print('[PAPER] Simulating futures trade:', signal['action'], symbol, 'qty:', quantity)
            # Simulate stop-loss/take-profit
            print(f"[PAPER] Would set stop-loss at {config.get('FUTURES_STOP_LOSS_PERCENT', 0)}% and take-profit at {config.get('FUTURES_TAKE_PROFIT_PERCENT', 0)}%.")
            # Update stats as if trade was filled
            realized_pnl = _get_today_realized_pnl(api_key, api_secret)
            stats = _load_daily_stats()
            stats['trades'] += 1
            stats['realized_pnl'] = realized_pnl
            _save_daily_stats(stats)
            return {
                'symbol': symbol,
                'side': side,
                'market': 'FUTURES',
                'confidence': signal.get('confidence', 0),
                'reason': '[PAPER] Trade executed (simulated)',
                'status': 'FILLED',
                'response': {'paper': True, 'action': side, 'quantity': quantity},
                'timestamp': datetime.now().isoformat()
            }
    
    if paper_trading:
        print('[PAPER] Simulating spot trade:', signal['action'], symbol, 'qty:', quantity)
        return {
            'symbol': symbol,
            'side': side,
            'market': 'SPOT',
            'confidence': signal.get('confidence', 0),
            'reason': '[PAPER] Trade executed (simulated)',
            'status': 'FILLED',
            'response': {'paper': True, 'action': side, 'quantity': quantity},
            'timestamp': datetime.now().isoformat()
        }
    
    params = {
        'symbol': symbol,
        'side': side,
        'type': 'MARKET',
        'quantity': quantity,
        'timestamp': int(time.time() * 1000)
    }
    
    query_string = urlencode(params)
    signature = _get_binance_signature(query_string, api_secret)
    params['signature'] = signature
    headers = {'X-MBX-APIKEY': api_key}
    
    try:
        response = requests.post(base_url + endpoint, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        trade_response = response.json()

        # --- Place stop-loss and take-profit for futures ---
        if signal.get('market') == 'FUTURES' and trade_response.get('orderId'):
            # Get entry price
            entry_price = None
            # Try to get fill price from response
            if 'avgFillPrice' in trade_response:
                entry_price = float(trade_response['avgFillPrice'])
            elif 'fills' in trade_response and len(trade_response['fills']) > 0:
                entry_price = float(trade_response['fills'][0].get('price', 0))
            elif 'price' in trade_response:
                entry_price = float(trade_response['price'])
            # If not found, fetch latest price
            if not entry_price or entry_price == 0:
                try:
                    price_url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
                    price_resp = requests.get(price_url, timeout=10)
                    price_resp.raise_for_status()
                    entry_price = float(price_resp.json()['price'])
                except Exception as e:
                    print(f"Entry price fetch error: {e}")
                    entry_price = None
            if entry_price:
                stop_loss_percent = config.get('FUTURES_STOP_LOSS_PERCENT', 0)
                take_profit_percent = config.get('FUTURES_TAKE_PROFIT_PERCENT', 0)
                if stop_loss_percent > 0:
                    if side == 'BUY':
                        stop_price = round(entry_price * (1 - stop_loss_percent / 100), 2)
                    else:
                        stop_price = round(entry_price * (1 + stop_loss_percent / 100), 2)
                    # Place stop-market order
                    sl_params = {
                        'symbol': symbol,
                        'side': 'SELL' if side == 'BUY' else 'BUY',
                        'type': 'STOP_MARKET',
                        'stopPrice': stop_price,
                        'closePosition': 'true',
                        'timestamp': int(time.time() * 1000)
                    }
                    sl_query = urlencode(sl_params)
                    sl_signature = _get_binance_signature(sl_query, api_secret)
                    sl_params['signature'] = sl_signature
                    try:
                        sl_resp = requests.post('https://fapi.binance.com/fapi/v1/order', headers=headers, params=sl_params, timeout=10)
                        sl_resp.raise_for_status()
                        print(f"Stop-loss order placed at {stop_price}")
                    except Exception as e:
                        print(f"Stop-loss order error: {e}")
                if take_profit_percent > 0:
                    if side == 'BUY':
                        tp_price = round(entry_price * (1 + take_profit_percent / 100), 2)
                    else:
                        tp_price = round(entry_price * (1 - take_profit_percent / 100), 2)
                    # Place take-profit-market order
                    tp_params = {
                        'symbol': symbol,
                        'side': 'SELL' if side == 'BUY' else 'BUY',
                        'type': 'TAKE_PROFIT_MARKET',
                        'stopPrice': tp_price,
                        'closePosition': 'true',
                        'timestamp': int(time.time() * 1000)
                    }
                    tp_query = urlencode(tp_params)
                    tp_signature = _get_binance_signature(tp_query, api_secret)
                    tp_params['signature'] = tp_signature
                    try:
                        tp_resp = requests.post('https://fapi.binance.com/fapi/v1/order', headers=headers, params=tp_params, timeout=10)
                        tp_resp.raise_for_status()
                        print(f"Take-profit order placed at {tp_price}")
                    except Exception as e:
                        print(f"Take-profit order error: {e}")

        # After a successful trade, update stats with actual realized PnL
        if signal.get('market') == 'FUTURES':
            realized_pnl = _get_today_realized_pnl(api_key, api_secret)
            stats = _load_daily_stats()
            stats['trades'] += 1
            stats['realized_pnl'] = realized_pnl
            _save_daily_stats(stats)

        return {
            'symbol': symbol,
            'side': side,
            'market': signal.get('market', 'SPOT'),
            'confidence': signal.get('confidence', 0),
            'reason': signal.get('reason', 'Trade executed successfully'),
            'status': 'FILLED',
            'response': trade_response,
            'timestamp': datetime.now().isoformat()
        }
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error: {e.response.status_code} - {e.response.text}"
        print(f"Binance API error: {error_msg}")
        return {
            'symbol': symbol,
            'side': side,
            'market': signal.get('market', 'SPOT'),
            'confidence': signal.get('confidence', 0),
            'reason': f"Trade failed: {error_msg}",
            'status': 'FAILED',
            'response': None,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Binance API error: {e}")
        return {
            'symbol': symbol,
            'side': side,
            'market': signal.get('market', 'SPOT'),
            'confidence': signal.get('confidence', 0),
            'reason': f"Trade failed: {e}",
            'status': 'FAILED',
            'response': None,
            'timestamp': datetime.now().isoformat()
        } 