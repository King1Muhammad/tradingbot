import requests
import json
import time

def get_trade_signal(market_data, gemini_api_key):
    """Get trade signal from Gemini 2.0 Flash AI based on market data"""
    if not gemini_api_key:
        return {
            "action": "HOLD", 
            "market": "SPOT", 
            "symbol": "BTCUSDT", 
            "confidence": 0, 
            "reason": "Gemini API key not configured"
        }
    
    try:
        # Use Gemini 2.0 Flash API endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"
        headers = {"Content-Type": "application/json"}
        
        # Create prompt
        prompt = f"""
        You are a crypto trading AI assistant. Analyze the following crypto market data and provide a trading recommendation.
        
        Market Data:
        {json.dumps(market_data, indent=2)}
        
        Respond with ONLY a valid JSON object containing these exact fields:
        - action: "BUY", "SELL", or "HOLD"
        - market: "SPOT" or "FUTURES" 
        - symbol: trading pair (e.g., "BTCUSDT", "ETHUSDT")
        - confidence: number between 0-100
        - reason: brief explanation of your decision
        
        Example response format:
        {{
            "action": "BUY",
            "market": "FUTURES", 
            "symbol": "BTCUSDT",
            "confidence": 75,
            "reason": "Strong upward momentum with high volume and volatility."
        }}
        
        Be proactive: If you see any reasonable opportunity, recommend BUY or SELL, and prefer FUTURES for strong trends or for shorting. Only use HOLD if there is truly no opportunity. Consider using FUTURES for both long and short trades, especially if the market is volatile or trending.
        """
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.4,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1024
            }
        }
        
        # Make API request
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()
        
        # Extract the model's text response
        if 'candidates' in result and len(result['candidates']) > 0:
            text = result['candidates'][0]['content']['parts'][0]['text']
        else:
            raise ValueError("No response content received from Gemini API")
        
        # Parse JSON response
        try:
            # Clean up the response if it contains markdown formatting
            response_text = text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            result = json.loads(response_text.strip())
            
            # Validate required fields
            required_fields = ['action', 'market', 'symbol', 'confidence', 'reason']
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate action
            if result['action'] not in ['BUY', 'SELL', 'HOLD']:
                result['action'] = 'HOLD'
                result['reason'] = f"Invalid action corrected to HOLD. Original: {result.get('reason', 'Unknown')}"
            
            # Validate market
            if result['market'] not in ['SPOT', 'FUTURES']:
                result['market'] = 'SPOT'
            
            # Validate confidence
            try:
                result['confidence'] = max(0, min(100, int(result['confidence'])))
            except (ValueError, TypeError):
                result['confidence'] = 0
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse Gemini response as JSON: {e}")
            print(f"Response text: {text}")
            return {
                "action": "HOLD",
                "market": "SPOT", 
                "symbol": "BTCUSDT",
                "confidence": 0,
                "reason": f"Failed to parse AI response: {e}"
            }
            
    except requests.exceptions.HTTPError as e:
        print(f"Gemini API HTTP error: {e.response.status_code} - {e.response.text}")
        return {
            "action": "HOLD",
            "market": "SPOT", 
            "symbol": "BTCUSDT",
            "confidence": 0,
            "reason": f"API HTTP error: {e.response.status_code}"
        }
    except Exception as e:
        print(f"Gemini API error: {e}")
        return {
            "action": "HOLD",
            "market": "SPOT", 
            "symbol": "BTCUSDT",
            "confidence": 0,
            "reason": f"AI service error: {e}"
        } 