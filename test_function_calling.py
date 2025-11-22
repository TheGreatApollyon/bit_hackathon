#!/usr/bin/env python3
"""Test Gemini function calling to debug the issue"""

import os
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

# Configure
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

print("Testing Gemini Function Calling...")
print("=" * 60)

# Test 1: Simple function with Python function
print("\nTest 1: Using Python function directly")
def multiply(a: float, b: float):
    """Multiply two numbers"""
    return a * b

try:
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        tools=[multiply]
    )
    
    result = model.generate_content('What is 12 times 8?')
    print(f"✓ Model created and responded")
    print(f"Response has text: {hasattr(result, 'text')}")
    if hasattr(result, 'text'):
        print(f"Text: {result.text}")
    
    if result.candidates:
        part = result.candidates[0].content.parts[0]
        if hasattr(part, 'function_call'):
            print(f"✓ Got function call: {part.function_call.name}")
            print(f"  Args: {dict(part.function_call.args)}")
        else:
            print("  No function call in response")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Using dictionary declaration  
print("\n" + "=" * 60)
print("Test 2: Using dictionary function declaration")

schedule_func = {
    'name': 'schedule_appointment',
    'description': 'Schedule a medical appointment for the patient',
    'parameters': {
        'type': 'object',
        'properties': {
            'department': {
                'type': 'string',
                'description': 'Medical department like Cardiology, Orthopedics, etc'
            },
            'preferred_date': {
                'type': 'string',
                'description': 'Preferred date in YYYY-MM-DD format'
            },
            'symptoms': {
                'type': 'string',
                'description': 'Brief description of symptoms or reason for visit'
            }
        },
        'required': ['department', 'symptoms']
    }
}

try:
    model2 = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        tools=[schedule_func]
    )
    
    result2 = model2.generate_content('I need to schedule a cardiology appointment for chest pain next Tuesday')
    print(f"✓ Model created and responded")
    
    if result2.candidates:
        part =  result2.candidates[0].content.parts[0]
        print(f"Part type: {type(part)}")
        print(f"Has function_call attr: {hasattr(part, 'function_call')}")
        
        if hasattr(part, 'function_call') and part.function_call:
            fc = part.function_call
            print(f"✓ Got function call: {fc.name}")
            print(f"  Args: {dict(fc.args)}")
        elif hasattr(part, 'text'):
            print(f"Text response: {part.text}")
        else:
            print(f"Unknown part type: {part}")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Testing complete!")
