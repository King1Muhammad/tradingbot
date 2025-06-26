import json
from datetime import datetime

def log_trade(trade_result, log_file='trade_log.jsonl'):
    entry = trade_result.copy()
    entry['timestamp'] = datetime.utcnow().isoformat()
    try:
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    except Exception as e:
        print(f"Logging error: {e}") 