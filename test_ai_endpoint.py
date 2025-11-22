#!/usr/bin/env python3
"""
Quick test of the AI assistant endpoint
Run this while the app is running to test the endpoint directly
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5001"

# Create a session and login
session = requests.Session()

print("Logging in as patient...")
login_response = session.post(f"{BASE_URL}/login", data={
    'email': 'patient@test.com',
    'password': 'password'
})

if login_response.status_code == 200:
    print("✓ Logged in successfully")
    
    # Test the AI assistant endpoint
    print("\nTesting AI assistant with scheduling request...")
    ai_response = session.post(
        f"{BASE_URL}/api/patient/ai-assistant",
        json={'query': 'I need to schedule a cardiology appointment for chest pain next week'}
    )
    
    print(f"\nResponse Status: {ai_response.status_code}")
    print(f"Response Headers: {dict(ai_response.headers)}")
    
    if ai_response.status_code == 200:
        try:
            data = ai_response.json()
            print("\n✓ Got JSON response:")
            print(json.dumps(data, indent=2))
            
            if data.get('action'):
                print("\n✅ SUCCESS! Function calling is working!")
                print(f"Function to call: {data['action']['function']}")
                print(f"Parameters: {json.dumps(data['action']['parameters'], indent=2)}")
            else:
                print("\n⚠ Got response but no action suggested")
                print(f"Response text: {data.get('response', 'No response')}")
        except Exception as e:
            print(f"\n❌ Error parsing JSON: {e}")
            print(f"Raw response: {ai_response.text[:500]}")
    else:
        print(f"\n❌ Request failed")
        print(f"Response: {ai_response.text[:500]}")
else:
    print(f"❌ Login failed: {login_response.status_code}")
    print(f"Response: {login_response.text[:200]}")

print("\n" + "="*60)
print("Note: If you see errors about old ai_assistant module,")
print("the app needs to be restarted to load the new version!")
print("="*60)
