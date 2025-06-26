import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode
from utils import load_config

def _get_binance_signature(query_string, secret):
    """Generate Binance API signature"""
    return hmac.new(secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

def get_spot_balance(config):
    """Get spot wallet balance"""
    if not config.get('BINANCE_API_KEY') or not config.get('BINANCE_API_SECRET'):
        return {"error": "Binance API keys not configured"}
    
    try:
        api_key = config['BINANCE_API_KEY']
        api_secret = config['BINANCE_API_SECRET']
        
        # Get account info
        url = "https://api.binance.com/api/v3/account"
        params = {
            'timestamp': int(time.time() * 1000)
        }
        
        query_string = urlencode(params)
        signature = _get_binance_signature(query_string, api_secret)
        params['signature'] = signature
        headers = {'X-MBX-APIKEY': api_key}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        account_info = response.json()
        
        # Filter balances with non-zero amounts
        balances = []
        for balance in account_info['balances']:
            free = float(balance['free'])
            locked = float(balance['locked'])
            total = free + locked
            
            if total > 0:  # Only show assets with balance
                balances.append({
                    'asset': balance['asset'],
                    'free': free,
                    'locked': locked,
                    'total': total
                })
        
        # Sort by total value (descending)
        balances.sort(key=lambda x: x['total'], reverse=True)
        
        return {
            'type': 'SPOT',
            'balances': balances,
            'total_assets': len(balances)
        }
        
    except Exception as e:
        return {"error": f"Failed to get spot balance: {e}"}

def get_futures_balance(config):
    """Get futures wallet balance"""
    if not config.get('BINANCE_API_KEY') or not config.get('BINANCE_API_SECRET'):
        return {"error": "Binance API keys not configured"}
    
    try:
        api_key = config['BINANCE_API_KEY']
        api_secret = config['BINANCE_API_SECRET']
        
        # Get futures account info
        url = "https://fapi.binance.com/fapi/v2/account"
        params = {
            'timestamp': int(time.time() * 1000)
        }
        
        query_string = urlencode(params)
        signature = _get_binance_signature(query_string, api_secret)
        params['signature'] = signature
        headers = {'X-MBX-APIKEY': api_key}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        account_info = response.json()
        
        # Get asset balances
        balances = []
        for asset in account_info['assets']:
            wallet_balance = float(asset['walletBalance'])
            if wallet_balance > 0:
                balances.append({
                    'asset': asset['asset'],
                    'wallet_balance': wallet_balance,
                    'unrealized_pnl': float(asset['unrealizedPnl']),
                    'margin_balance': float(asset['marginBalance'])
                })
        
        # Sort by wallet balance (descending)
        balances.sort(key=lambda x: x['wallet_balance'], reverse=True)
        
        return {
            'type': 'FUTURES',
            'balances': balances,
            'total_assets': len(balances),
            'total_wallet_balance': account_info.get('totalWalletBalance', 0),
            'total_unrealized_pnl': account_info.get('totalUnrealizedPnl', 0)
        }
        
    except Exception as e:
        return {"error": f"Failed to get futures balance: {e}"}

def get_all_balances():
    """Get both spot and futures balances"""
    config = load_config()
    
    print("💰 Checking Wallet Balances...")
    print("=" * 50)
    
    # Get spot balance
    spot_result = get_spot_balance(config)
    if 'error' in spot_result:
        print(f"❌ Spot Balance Error: {spot_result['error']}")
    else:
        print(f"📊 SPOT WALLET ({spot_result['total_assets']} assets):")
        for balance in spot_result['balances']:
            print(f"  {balance['asset']}: {balance['total']:.8f} (Free: {balance['free']:.8f}, Locked: {balance['locked']:.8f})")
    
    print()
    
    # Get futures balance
    futures_result = get_futures_balance(config)
    if 'error' in futures_result:
        print(f"❌ Futures Balance Error: {futures_result['error']}")
    else:
        print(f"📈 FUTURES WALLET ({futures_result['total_assets']} assets):")
        for balance in futures_result['balances']:
            print(f"  {balance['asset']}: {balance['wallet_balance']:.8f} (Unrealized PnL: {balance['unrealized_pnl']:.8f})")
        
        if futures_result['total_assets'] > 0:
            print(f"\n📊 Total Wallet Balance: {futures_result['total_wallet_balance']:.8f} USDT")
            print(f"📊 Total Unrealized PnL: {futures_result['total_unrealized_pnl']:.8f} USDT")
    
    print("=" * 50)
    
    return {
        'spot': spot_result,
        'futures': futures_result
    }

if __name__ == "__main__":
    get_all_balances() 