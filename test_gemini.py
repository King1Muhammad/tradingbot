#!/usr/bin/env python3
"""
Test script for Gemini 2.0 Flash API
This script tests the API connection and response parsing
"""

import json
import requests
from utils import load_config

def test_gemini_api():
    """Test Gemini 2.0 Flash API with actual API key"""
    print("🧪 Testing Gemini 2.0 Flash API...")
    
    # Load configuration
    config = load_config()
    api_key = config.get('GEMINI_API_KEY')
    
    if not api_key or api_key == 'your_gemini_api_key_here':
        print("❌ No valid Gemini API key found in .env file")
        print("Please add your Gemini 2.0 Flash API key to the .env file")
        return False
    
    try:
        # Test API endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        
        # Simple test prompt
        prompt = """
        Respond with ONLY a valid JSON object containing these exact fields:
        - action: "HOLD"
        - market: "SPOT" 
        - symbol: "BTCUSDT"
        - confidence: 0
        - reason: "Test response"
        """
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 256
            }
        }
        
        print("📡 Making API request...")
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        
        result = response.json()
        print("✅ API request successful")
        
        # Extract response text
        if 'candidates' in result and len(result['candidates']) > 0:
            text = result['candidates'][0]['content']['parts'][0]['text']
            print(f"📝 Response: {text}")
            
            # Try to parse JSON
            try:
                # Clean up response
                response_text = text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                parsed = json.loads(response_text.strip())
                print(f"✅ JSON parsed successfully: {parsed}")
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON: {e}")
                print(f"Raw response: {text}")
                return False
        else:
            print("❌ No response content received")
            print(f"API response: {result}")
            return False
            
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🤖 Gemini 2.0 Flash API Test")
    print("=" * 40)
    
    if test_gemini_api():
        print("\n🎉 Gemini 2.0 Flash API test PASSED!")
        print("Your API key is working correctly.")
    else:
        print("\n❌ Gemini 2.0 Flash API test FAILED!")
        print("Please check your API key and try again.")

if __name__ == "__main__":
    main() 