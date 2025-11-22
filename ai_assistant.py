"""
AI Assistant Module for HealthCredX
Works with google-generativeai 0.8.5+
Uses Python functions for function calling
"""

import os
import json
from datetime import datetime, timedelta
import google.generativeai as genai
from typing import Dict, List, Any, Optional

# Configure Gemini API
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# ============================================================
# PATIENT AI ASSISTANT WITH FUNCTION CALLING
# ============================================================

def patient_assistant(user_query: str, patient_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    AI assistant for patients - handles appointment scheduling
    """
    if not api_key:
        return {"response": "AI service is currently unavailable.", "action": None}
    
    try:
        # Define functions that AI can call
        def schedule_appointment(department: str, symptoms: str, preferred_date: str = "", preferred_time: str = "morning"):
            """Schedule a new medical appointment.
            
            Args:
                department: Medical department (Cardiology, Orthopedics, etc.)
                symptoms: Description of symptoms or reason for visit
                preferred_date: Preferred date in YYYY-MM-DD format
                preferred_time: Time slot (morning, afternoon, evening)
            """
            return {"department": department, "symptoms": symptoms, "preferred_date": preferred_date, "preferred_time": preferred_time}
        
        def reschedule_appointment(appointment_id: int, new_date: str, new_time: str = "morning"):
            """Reschedule an existing appointment.
            
            Args:
                appointment_id: ID of appointment to reschedule
                new_date: New date in YYYY-MM-DD format
                new_time: New time slot (morning, afternoon, evening)
            """
            return {"appointment_id": appointment_id, "new_date": new_date, "new_time": new_time}
        
        def cancel_appointment(appointment_id: int, reason: str = ""):
            """Cancel an existing appointment.
            
            Args:
                appointment_id: ID of appointment to cancel
                reason: Optional cancellation reason
            """
            return {"appointment_id": appointment_id, "reason": reason}
        
        # Build context
        appointments_info = ""
        appts = context.get('appointments', [])
        if appts:
            appointments_info = "Current Appointments:\n"
            for a in appts:
                appointments_info += f"- ID:{a.get('id')}, Date:{a.get('date_time','N/A')}, Dept:{a.get('department','N/A')}\n"
        else:
            appointments_info = "No appointments scheduled."
        
        history = context.get('medical_history', 'No medical history')
        
        prompt = f"""You are a medical assistant helping a patient.

{appointments_info}

Medical History:
{history}

Patient Query: {user_query}

Use the available functions to help schedule, reschedule, or cancel appointments as needed."""
        
        # Create model with functions as tools
        model =  genai.GenerativeModel('gemini-2.5-flash', tools=[schedule_appointment, reschedule_appointment, cancel_appointment])
        
        # Generate response
        response = model.generate_content(prompt)
        
        # Check for function call
        for part in response.parts:
            if fn := part.function_call:
                # Extract args
                args = {key: val for key, val in fn.args.items()}
                
                return {
                    "response": "I can help you with that. Please confirm:",
                    "action": {
                        "type": "function_call",
                        "function": fn.name,
                        "parameters": args
                    },
                    "requires_confirmation": True
                }
        
        # No function call, return text
        return {"response": response.text, "action": None}
            
    except Exception as e:
        print(f"❌ Error in patient_assistant: {e}")
        import traceback
        traceback.print_exc()
        return {"response": f"Error: {str(e)}", "action": None}

# ============================================================
# OTHER AI FUNCTIONS
# ============================================================

def get_diagnosis_suggestions(symptoms: str, patient_history: str = "") -> Dict[str, Any]:
    """Get AI diagnosis suggestions"""
    if not api_key:
        return {"error": "AI unavailable"}
    try:
        model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
        prompt = f"""Medical AI. Symptoms: {symptoms}. History: {patient_history}.
Provide top 3 diagnoses, tests, red flags, treatment. JSON format:
{{"differential_diagnoses":[{{"condition":"","probability":"","reasoning":""}}],"recommended_tests":[],"red_flags":[],"treatment_considerations":[],"disclaimer":""}}"""
        response = model.generate_content(prompt)
        return {"success": True, "suggestions": json.loads(response.text)}
    except Exception as e:
        return {"error": str(e)}

def check_prescription_safety(medications: List[str], patient_conditions: str = "") -> Dict[str, Any]:
    """Check prescription safety"""
    if not api_key:
        return {"error": "AI unavailable"}
    try:
        model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
        prompt = f"""Analyze safety: {', '.join(medications)}. Conditions: {patient_conditions}.
JSON: {{"safe":true/false,"risk_level":"","interactions":[],"contraindications":[],"warnings":[],"alternatives":[],"recommendations":""}}"""
        response = model.generate_content(prompt)
        return {"success": True, "safety_check": json.loads(response.text)}
    except Exception as e:
        return {"error": str(e)}

def smart_triage(symptoms: str, patient_info: Dict[str, Any]) -> Dict[str, Any]:
    """AI patient triage"""
    if not api_key:
        return {"error": "AI unavailable"}
    try:
        model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
        prompt = f"""Triage. Symptoms: {symptoms}. Info: {json.dumps(patient_info)}.
JSON: {{"urgency":"","recommended_department":"","reasoning":"","wait_time_recommendation":"","pre_consultation_instructions":[],"emergency_warning":""}}"""
        response = model.generate_content(prompt)
        return {"success": True, "triage": json.loads(response.text)}
    except Exception as e:
        return {"error": str(e)}

def forecast_inventory_demand(inventory_data: List[Dict], prescription_history: List[Dict]) -> Dict[str, Any]:
    """Inventory forecasting"""
    if not api_key:
        return {"error": "AI unavailable"}
    try:
        model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
        prompt = f"""Inventory forecast. Stock: {json.dumps(inventory_data[:10])}. Prescriptions: {json.dumps(prescription_history[:10])}.
JSON: {{"low_stock_alerts":[],"demand_trends":{{"increasing":[],"decreasing":[],"stable":[]}},"recommendations":[]}}"""
        response = model.generate_content(prompt)
        return {"success": True, "forecast": json.loads(response.text)}
    except Exception as e:
        return {"error": str(e)}

def practitioner_assistant(user_query: str, practitioner_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
    """AI for practitioners"""
    if not api_key:
        return {"response": "AI unavailable", "action": None}
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(f"Medical AI for practitioner. Query: {user_query}")
        return {"response": response.text, "action": None}
    except Exception as e:
        return {"response": str(e), "action": None}

def hospital_assistant(user_query: str, hospital_id: int, context: Dict[str, Any]) -> str:
    """AI for hospitals"""
    if not api_key:
        return "AI unavailable"
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(f"Hospital AI. Query: {user_query}")
        return response.text
    except Exception as e:
        return str(e)

def pharma_assistant(user_query: str, pharma_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
    """AI for pharmacies"""
    if not api_key:
        return {"response": "AI unavailable", "action": None}
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(f"Pharmacy AI. Query: {user_query}")
        return {"response": response.text, "action": None}
    except Exception as e:
        return {"response": str(e), "action": None}

def organization_assistant(user_query: str, org_id: int, context: Dict[str, Any]) -> str:
    """AI for organizations"""
    if not api_key:
        return "AI unavailable"
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(f"Organization AI. Query: {user_query}")
        return response.text
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    print("✓ AI Assistant Module")
    if api_key:
        print("✓ API configured")
        result = patient_assistant("Schedule cardiology appointment", 1, {'appointments': [], 'medical_history': ''})
        print(f"Test: {result}")
    else:
        print("✗ No API key")
