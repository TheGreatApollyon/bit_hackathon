import requests
import os

BASE_URL = "http://127.0.0.1:5001"

def test_patient_chat():
    print("\n--- Testing Patient Chat ---")
    session = requests.Session()
    
    # Login
    login_payload = {'email': 'patient@test.com', 'password': 'password'}
    response = session.post(f"{BASE_URL}/login", data=login_payload)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    # Chat
    chat_payload = {'query': 'What was my last diagnosis?'}
    response = session.post(f"{BASE_URL}/api/patient/chat", json=chat_payload)
    
    if response.status_code == 200:
        print("Chat Response:", response.json())
        if "Grade 1 Ankle Sprain" in str(response.json()):
            print("✓ Chat verification SUCCESS")
        else:
            print("⚠ Chat verification response content mismatch (but API worked)")
    else:
        print(f"Chat failed: {response.status_code} - {response.text}")

def test_document_upload():
    print("\n--- Testing Document Upload ---")
    session = requests.Session()
    
    # Login
    login_payload = {'email': 'doctor@test.com', 'password': 'password'}
    response = session.post(f"{BASE_URL}/login", data=login_payload)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
        
    # Upload
    file_path = "/Users/sam/.gemini/antigravity/brain/cfdeb6d6-7c71-47cf-88c8-51fa44bf1367/test_medical_certificate_1763748812741.png"
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    files = {
        'documents': ('certificate.png', open(file_path, 'rb'), 'image/png')
    }
    data = {
        'document_types': 'Medical Degree'
    }
    
    response = session.post(f"{BASE_URL}/practitioner/upload", files=files, data=data)
    
    if response.status_code == 200:
        print("Upload Response:", response.json())
        if response.json().get('success'):
            print("✓ Document upload verification SUCCESS")
        else:
            print("✗ Document upload failed in API logic")
    else:
        print(f"Upload failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    try:
        test_patient_chat()
        test_document_upload()
    except Exception as e:
        print(f"Verification script error: {e}")
