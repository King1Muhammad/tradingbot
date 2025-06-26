#!/usr/bin/env python3
"""
Simple script to check your Binance wallet balances
"""

from wallet_checker import get_all_balances
from utils import load_config

def main():
    print("🤖 Binance Wallet Balance Checker")
    print("=" * 50)
    
    # Check if API keys are configured
    config = load_config()
    if not config.get('BINANCE_API_KEY') or not config.get('BINANCE_API_SECRET'):
        print("❌ Binance API keys not configured!")
        print("Please add your Binance API keys to the .env file:")
        print("BINANCE_API_KEY=your_api_key_here")
        print("BINANCE_API_SECRET=your_api_secret_here")
        return
    
    # Get balances
    balances = get_all_balances()
    
    # Summary
    print("\n📋 SUMMARY:")
    spot_assets = len(balances['spot'].get('balances', [])) if 'error' not in balances['spot'] else 0
    futures_assets = len(balances['futures'].get('balances', [])) if 'error' not in balances['futures'] else 0
    
    print(f"  Spot Assets: {spot_assets}")
    print(f"  Futures Assets: {futures_assets}")
    
    if futures_assets > 0 and 'total_wallet_balance' in balances['futures']:
        total_balance = balances['futures']['total_wallet_balance']
        total_pnl = balances['futures']['total_unrealized_pnl']
        print(f"  Total Futures Balance: {total_balance:.2f} USDT")
        print(f"  Total Unrealized PnL: {total_pnl:.2f} USDT")

if __name__ == "__main__":
    main() 