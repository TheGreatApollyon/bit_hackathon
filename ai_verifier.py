"""
AI-powered document verification using Google Gemini 2.5 Flash
Analyzes medical credentials and provides authenticity scoring
"""

import os
import google.generativeai as genai
from PIL import Image
import json
from pathlib import Path

# Configure Gemini API
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    # Use the requested Gemini 2.5 Flash model
    try:
        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            generation_config={"response_mime_type": "application/json"}
        )
    except:
        # Fallback if specific version issue, though list confirmed it exists
        model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

def analyze_medical_document(image_path, document_type="Medical Document"):
    """
    Analyze a medical credential document using Gemini Vision
    
    Args:
        image_path: Path to the document image
        document_type: Type of document (degree, license, certificate)
    
    Returns:
        dict: Analysis results with authenticity score and details
    """
    if not model:
        return {
            "error": "Gemini API not configured",
            "authenticity_score": 0,
            "analysis": "AI analysis unavailable - API key not set"
        }
    
    try:
        # Load image
        img = Image.open(image_path)
        
        # Construct detailed prompt for medical document analysis
        prompt = f"""You are an expert document verification specialist for medical credentials.

Analyze this {document_type} image carefully and provide a detailed assessment.

Evaluate the following aspects:
1. **Document Authenticity** (0-100 score):
   - Quality and clarity of the image
   - Presence of official seals, stamps, or watermarks
   - Professional formatting and layout
   - Consistency of fonts and design
   - Signs of tampering or forgery

2. **Content Extraction**:
   - Institution/Organization name
   - Holder's name (if visible)
   - Issue date (if visible)
   - Expiration date (if applicable)
   - Credentials/qualifications mentioned
   - License/Registration numbers (if present)

3. **Risk Assessment**:
   - Any red flags or concerns
   - Recommendations for further verification

Output must be a JSON object with this schema:
{{
    "authenticity_score": int,
    "document_type": str,
    "issuing_institution": str,
    "holder_name": str,
    "issue_date": str,
    "expiration_date": str,
    "credentials_mentioned": list[str],
    "verification_notes": str,
    "concerns": list[str],
    "recommendation": str
}}
"""

        # Generate content with the image
        response = model.generate_content([img, prompt])
        
        # Parse response - with response_mime_type="application/json", 
        # the text should be valid JSON directly
        try:
            analysis = json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback cleanup if model adds markdown blocks despite config
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
            analysis = json.loads(text.strip())
        
        return {
            "success": True,
            "authenticity_score": analysis.get("authenticity_score", 0),
            "analysis": analysis
        }
        
    except Exception as e:
        return {
            "error": f"AI analysis failed: {str(e)}",
            "authenticity_score": 0
        }

def chat_with_history(context, user_query):
    """
    Chat with the AI using medical history as context.
    """
    if not api_key:
        return "AI service is currently unavailable."

    try:
        chat_model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = f"""
        You are a helpful medical assistant for a patient.
        Here is the patient's medical history context:
        {context}
        
        User Query: {user_query}
        
        Answer the query based on the context provided. Be empathetic, clear, and professional. 
        If the answer is not in the context, say you don't have that information.
        Do not provide medical advice that contradicts the doctor's notes.
        """
        
        response = chat_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error in chat_with_history: {e}")
        return "I'm sorry, I encountered an error processing your request."

def batch_analyze_documents(document_paths):
    """
    Analyze multiple documents and return aggregated results
    
    Args:
        document_paths: List of tuples (path, document_type)
    
    Returns:
        dict: Aggregated analysis results
    """
    results = []
    total_score = 0
    
    for path, doc_type in document_paths:
        result = analyze_medical_document(path, doc_type)
        results.append({
            "document_type": doc_type,
            "result": result
        })
        if "authenticity_score" in result:
            total_score += result["authenticity_score"]
    
    avg_score = total_score / len(document_paths) if document_paths else 0
    
    return {
        "average_score": round(avg_score),
        "individual_results": results,
        "total_documents": len(document_paths)
    }

def get_verification_summary(analysis_result):
    """
    Generate human-readable summary from analysis
    
    Args:
        analysis_result: Result from analyze_medical_document
    
    Returns:
        str: Summary text
    """
    if "error" in analysis_result:
        return f"Analysis Error: {analysis_result['error']}"
    
    analysis = analysis_result.get("analysis", {})
    score = analysis_result.get("authenticity_score", 0)
    
    summary = f"Authenticity Score: {score}/100\n\n"
    
    if score >= 80:
        summary += "✓ Document appears highly authentic\n"
    elif score >= 60:
        summary += "⚠ Document appears moderately authentic - manual review recommended\n"
    else:
        summary += "✗ Document has significant concerns - thorough review required\n"
    
    if analysis.get("verification_notes"):
        summary += f"\n{analysis['verification_notes']}\n"
    
    if analysis.get("concerns"):
        summary += f"\nConcerns: {', '.join(analysis['concerns'])}"
    
    return summary

# For testing
if __name__ == '__main__':
    print("Gemini AI Verifier initialized")
    if model:
        print(f"✓ Model ready: {model.model_name}")
    else:
        print("✗ API key not configured")
