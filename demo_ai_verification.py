#!/usr/bin/env python3
"""
Demo script to showcase the AI Document Verification workflow
This demonstrates how the system works once the Gemini API key is added
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check if environment is properly configured"""
    print("=" * 70)
    print("HealthCredX AI Document Verification - Environment Check")
    print("=" * 70)
    
    # Check Gemini API Key
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key and api_key != 'your_gemini_api_key_here':
        print("✓ GEMINI_API_KEY is configured")
        print(f"  Key preview: {api_key[:20]}...")
    else:
        print("✗ GEMINI_API_KEY not set")
        print("  Please add your API key to the .env file")
        print("  Get it from: https://makersuite.google.com/app/apikey")
    
    # Check Secret Key
    secret_key = os.getenv('SECRET_KEY')
    if secret_key and secret_key != 'your_secret_key_for_flask_sessions_here':
        print("✓ SECRET_KEY is configured")
    else:
        print("⚠ SECRET_KEY using default (recommended to change for production)")
    
    print()

def demonstrate_workflow():
    """Demonstrate the AI verification workflow"""
    print("=" * 70)
    print("AI Document Verification Workflow")
    print("=" * 70)
    print()
    
    print("STEP 1: Practitioner Uploads Documents")
    print("  → Medical degree certificate")
    print("  → License document")
    print("  → Professional certifications")
    print()
    
    print("STEP 2: AI Analysis (Gemini 2.5 Flash)")
    print("  → Each document analyzed for authenticity")
    print("  → Structured output generated with:")
    print("     • Authenticity Score (0-100)")
    print("     • Document Type Detection")
    print("     • Issuing Institution Extraction")
    print("     • Verification Notes")
    print("     • Risk Assessment & Concerns")
    print("     • Recommendation (approve/review/reject)")
    print()
    
    print("STEP 3: Organization Review")
    print("  → Organization sees AI analysis results")
    print("  → Reviews documents with AI insights")
    print("  → Makes preliminary verdict:")
    print("     • APPROVED → Forward to Admin")
    print("     • REJECTED → Send back to practitioner")
    print()
    
    print("STEP 4: Admin Final Decision")
    print("  → Admin reviews org-approved verifications")
    print("  → Sees full AI analysis + org comments")
    print("  → Makes final decision:")
    print("     • APPROVE → Issue blockchain credential")
    print("     • DISMISS → Reject verification")
    print()
    
    print("=" * 70)
    print("Example AI Analysis Output (JSON Structure)")
    print("=" * 70)
    
    example_output = """
{
  "authenticity_score": 92,
  "document_type": "Medical Degree Certificate",
  "issuing_institution": "Harvard Medical School",
  "holder_name": "Dr. Jane Smith",
  "issue_date": "2020-06-15",
  "expiration_date": "N/A",
  "credentials_mentioned": [
    "Doctor of Medicine (M.D.)",
    "Cum Laude"
  ],
  "verification_notes": "Document appears highly authentic with clear institutional seals, professional formatting, and consistent typography. Official Harvard Medical School watermark visible.",
  "concerns": [],
  "recommendation": "approve"
}
    """
    print(example_output)
    print()

def demonstrate_scoring():
    """Show how scoring works"""
    print("=" * 70)
    print("AI Authenticity Scoring System")
    print("=" * 70)
    print()
    
    print("Score Range  | Assessment          | Action")
    print("-------------|---------------------|----------------------------")
    print("80-100       | Highly Authentic    | ✓ Recommend approval")
    print("60-79        | Moderately Authentic| ⚠ Manual review recommended")
    print("0-59         | Significant Concerns| ✗ Thorough review required")
    print()
    
    print("Scoring Criteria:")
    print("  • Image quality and clarity")
    print("  • Presence of official seals/stamps/watermarks")
    print("  • Professional formatting and layout")
    print("  • Font consistency and design")
    print("  • Signs of tampering or forgery")
    print()

def test_ai_module():
    """Test if AI verifier module can be imported"""
    print("=" * 70)
    print("Testing AI Verifier Module")
    print("=" * 70)
    print()
    
    try:
        import ai_verifier
        print("✓ ai_verifier.py imported successfully")
        
        # Check if API key is configured
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key and api_key != 'your_gemini_api_key_here':
            print("✓ Gemini API is configured and ready")
            print()
            print("You can now:")
            print("  1. Start the application: python app.py")
            print("  2. Register as a practitioner")
            print("  3. Upload medical credential documents")
            print("  4. See AI analysis in real-time!")
        else:
            print("⚠ Waiting for GEMINI_API_KEY in .env file")
            print()
            print("Next steps:")
            print("  1. Get API key from: https://makersuite.google.com/app/apikey")
            print("  2. Add to .env file: GEMINI_API_KEY=your_actual_key_here")
            print("  3. Restart the application")
        
        print()
        
    except Exception as e:
        print(f"✗ Error importing ai_verifier: {e}")
        print()

if __name__ == '__main__':
    check_environment()
    print()
    
    demonstrate_workflow()
    demonstrate_scoring()
    test_ai_module()
    
    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)
