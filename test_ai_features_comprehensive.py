#!/usr/bin/env python3
"""
Comprehensive AI Features Test
Tests all AI assistant features for all user types
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5001"

def test_patient_ai_assistant():
    """Test patient AI assistant with appointment scheduling"""
    print("\n" + "="*60)
    print("Testing Patient AI Assistant")
    print("="*60)
    
    session = requests.Session()
    
    # Login as patient
    response = session.post(f"{BASE_URL}/login", data={
        'email': 'patient@test.com',
        'password': 'password'
    })
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return
    
    print("✓ Logged in as patient")
    
    # Test 1: Ask about medical history
    print("\n1. Testing medical history query...")
    response = session.post(f"{BASE_URL}/api/patient/ai-assistant", 
                           json={'query': 'What was my last diagnosis?'})
    if response.status_code == 200:
        data = response.json()
        print(f"✓ AI Response: {data.get('response', '')[:100]}...")
    else:
        print(f"❌ Failed: {response.status_code}")
    
    # Test 2: Request appointment scheduling
    print("\n2. Testing appointment scheduling request...")
    response = session.post(f"{BASE_URL}/api/patient/ai-assistant",
                           json={'query': 'I need to schedule a cardiology appointment next week'})
    if response.status_code == 200:
        data = response.json()
        print(f"✓ AI Response: {data.get('response', '')}")
        if data.get('action'):
            print(f"  Action requested: {data['action']['function']}")
            print(f"  Parameters: {json.dumps(data['action']['parameters'], indent=2)}")
        else:
            print("  Note: No action suggested (might need better prompt)")
    else:
        print(f"❌ Failed: {response.status_code}")
    
    session.get(f"{BASE_URL}/logout")

def test_practitioner_ai_features():
    """Test practitioner AI features"""
    print("\n" + "="*60)
    print("Testing Practitioner AI Features")
    print("="*60)
    
    session = requests.Session()
    
    # Login as practitioner
    response = session.post(f"{BASE_URL}/login", data={
        'email': 'doctor@test.com',
        'password': 'password'
    })
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return
    
    print("✓ Logged in as practitioner")
    
    # Test 1: General AI assistant
    print("\n1. Testing practitioner AI assistant...")
    response = session.post(f"{BASE_URL}/api/practitioner/ai-assistant",
                           json={'query': 'What are my appointments today?'})
    if response.status_code == 200:
        data = response.json()
        print(f"✓ AI Response: {data.get('response', '')[:100]}...")
    else:
        print(f"❌ Failed: {response.status_code}")
    
    # Test 2: Diagnosis suggestions
    print("\n2. Testing diagnosis suggestions...")
    response = session.post(f"{BASE_URL}/api/practitioner/diagnosis-suggestions",
                           json={
                               'symptoms': 'chest pain, shortness of breath, fatigue',
                               'patient_id': 1
                           })
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            suggestions = data['suggestions']
            print(f"✓ Got {len(suggestions.get('differential_diagnoses', []))} diagnosis suggestions")
            if suggestions.get('differential_diagnoses'):
                print(f"  Top diagnosis: {suggestions['differential_diagnoses'][0].get('condition', 'N/A')}")
        else:
            print(f"  Note: {data.get('error', 'No suggestions')}")
    else:
        print(f"❌ Failed: {response.status_code}")
    
    # Test 3: Prescription safety check
    print("\n3. Testing prescription safety check...")
    response = session.post(f"{BASE_URL}/api/practitioner/prescription-check",
                           json={
                               'medications': ['Aspirin', 'Warfarin', 'Ibuprofen'],
                               'patient_id': 1
                           })
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            safety = data['safety_check']
            print(f"✓ Safety check complete")
            print(f"  Risk level: {safety.get('risk_level', 'unknown')}")
            print(f"  Safe: {safety.get('safe', 'unknown')}")
            if safety.get('interactions'):
                print(f"  Interactions found: {len(safety['interactions'])}")
        else:
            print(f"  Note: {data.get('error', 'Check failed')}")
    else:
        print(f"❌ Failed: {response.status_code}")
    
    session.get(f"{BASE_URL}/logout")

def test_hospital_ai_features():
    """Test hospital AI features"""
    print("\n" + "="*60)
    print("Testing Hospital AI Features")
    print("="*60)
    
    session = requests.Session()
    
    # Login as hospital
    response = session.post(f"{BASE_URL}/login", data={
        'email': 'hospital@test.com',
        'password': 'password'
    })
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return
    
    print("✓ Logged in as hospital")
    
    # Test 1: Hospital AI assistant
    print("\n1. Testing hospital AI assistant...")
    response = session.post(f"{BASE_URL}/api/hospital/ai-assistant",
                           json={'query': 'What is our appointment load today?'})
    if response.status_code == 200:
        data = response.json()
        print(f"✓ AI Response: {data.get('response', '')[:100]}...")
    else:
        print(f"❌ Failed: {response.status_code}")
    
    # Test 2: Smart triage
    print("\n2. Testing smart triage...")
    response = session.post(f"{BASE_URL}/api/hospital/smart-triage",
                           json={
                               'symptoms': 'severe chest pain, difficulty breathing',
                               'patient_id': 1
                           })
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            triage = data['triage']
            print(f"✓ Triage complete")
            print(f"  Urgency: {triage.get('urgency', 'unknown')}")
            print(f"  Department: {triage.get('recommended_department', 'unknown')}")
        else:
            print(f"  Note: {data.get('error', 'Triage failed')}")
    else:
        print(f"❌ Failed: {response.status_code}")
    
    session.get(f"{BASE_URL}/logout")

def test_pharma_ai_features():
    """Test pharmacy AI features"""
    print("\n" + "="*60)
    print("Testing Pharmacy AI Features")
    print("="*60)
    
    session = requests.Session()
    
    # Login as pharma
    response = session.post(f"{BASE_URL}/login", data={
        'email': 'pharma@test.com',
        'password': 'password'
    })
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return
    
    print("✓ Logged in as pharmacy")
    
    # Test 1: Pharma AI assistant
    print("\n1. Testing pharma AI assistant...")
    response = session.post(f"{BASE_URL}/api/pharma/ai-assistant",
                           json={'query': 'What items are low in stock?'})
    if response.status_code == 200:
        data = response.json()
        print(f"✓ AI Response: {data.get('response', '')[:100]}...")
    else:
        print(f"❌ Failed: {response.status_code}")
    
    # Test 2: Inventory forecasting
    print("\n2. Testing inventory forecasting...")
    response = session.post(f"{BASE_URL}/api/pharma/inventory-forecast")
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            forecast = data['forecast']
            print(f"✓ Forecast complete")
            if forecast.get('low_stock_alerts'):
                print(f"  Low stock alerts: {len(forecast['low_stock_alerts'])}")
        else:
            print(f"  Note: {data.get('error', 'Forecast failed')}")
    else:
        print(f"❌ Failed: {response.status_code}")
    
    session.get(f"{BASE_URL}/logout")

def test_ai_module_initialization():
    """Test that AI modules are properly initialized"""
    print("\n" + "="*60)
    print("Testing AI Module Initialization")
    print("="*60)
    
    try:
        import ai_assistant
        print("✓ ai_assistant module imported successfully")
        
        # Check if API key is configured
        if ai_assistant.api_key:
            print("✓ Gemini API key is configured")
        else:
            print("⚠ Gemini API key not found (AI features will not work)")
            
    except ImportError as e:
        print(f"❌ Failed to import ai_assistant: {e}")

if __name__ == '__main__':
    print("\n" + "🤖 HealthCredX AI Features Comprehensive Test")
    print("=" * 60)
    
    # Test module initialization first
    test_ai_module_initialization()
    
    # Test all user type AI features
    test_patient_ai_assistant()
    test_practitioner_ai_features()
    test_hospital_ai_features()
    test_pharma_ai_features()
    
    print("\n" + "="*60)
    print("✅ All AI feature tests completed!")
    print("="*60)
    print("\nNote: Some tests may show 'Note:' messages if AI API is not configured.")
    print("This is expected behavior when GEMINI_API_KEY is not set.")
