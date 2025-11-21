import unittest
import os
import tempfile
from app import app, db, blockchain
import database

class HealthCredXExpansionTest(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['DATABASE'] = self.db_path
        
        from pathlib import Path
        # Override DB path for testing
        database.DB_PATH = Path(self.db_path)
        
        self.client = app.test_client()
        with app.app_context():
            database.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_full_flow(self):
        # 1. Register Hospital
        print("\n--- Testing Hospital Registration ---")
        resp = self.client.post('/register', data={
            'email': 'hospital@test.com',
            'password': 'password',
            'name': 'City Hospital',
            'role': 'hospital',
            'organization_name': 'City Hospital Group'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', resp.data)

        # Login Hospital
        self.client.post('/login', data={'email': 'hospital@test.com', 'password': 'password'}, follow_redirects=True)
        
        # 2. Onboard Patient
        print("--- Testing Patient Onboarding ---")
        resp = self.client.post('/hospital/onboard-patient', data={
            'email': 'patient@test.com',
            'password': 'password',
            'name': 'John Doe',
            'aadhar': '123456789012',
            'dob': '1990-01-01',
            'gender': 'Male',
            'blood_type': 'O+',
            'weight': '70',
            'height': '175',
            'conditions': 'None'
        }, follow_redirects=True)
        self.assertIn(b'Patient onboarded successfully', resp.data)

        # 3. Register Doctor
        print("--- Testing Doctor Registration ---")
        self.client.get('/logout')
        self.client.post('/register', data={
            'email': 'doctor@test.com',
            'password': 'password',
            'name': 'Dr. Smith',
            'role': 'practitioner',
            'practitioner_type': 'Cardiologist'
        }, follow_redirects=True)

        # 4. Schedule Appointment (Hospital)
        print("--- Testing Appointment Scheduling ---")
        self.client.post('/login', data={'email': 'hospital@test.com', 'password': 'password'}, follow_redirects=True)
        resp = self.client.post('/hospital/schedule-appointment', data={
            'patient_email': 'patient@test.com',
            'doctor_email': 'doctor@test.com',
            'date_time': '2025-12-01T10:00',
            'department': 'Cardiology'
        }, follow_redirects=True)
        self.assertIn(b'Appointment scheduled', resp.data)

        # 5. Doctor Visit (Diagnosis & Prescription)
        print("--- Testing Doctor Visit & Blockchain ---")
        self.client.get('/logout')
        self.client.post('/login', data={'email': 'doctor@test.com', 'password': 'password'}, follow_redirects=True)
        
        # Get appointment ID
        with app.app_context():
            doctor = database.get_user_by_email('doctor@test.com')
            appts = database.get_appointments_by_user(doctor['id'], 'practitioner')
            appt_id = appts[0]['id']

        resp = self.client.post(f'/practitioner/visit/{appt_id}', data={
            'diagnosis': 'Mild Hypertension',
            'prescription': 'Lisinopril 10mg',
            'signature': 'Dr. Smith Digital Sign'
        }, follow_redirects=True)
        self.assertIn(b'Visit recorded and secured on blockchain', resp.data)

        # Verify Blockchain
        with app.app_context():
            latest_block = blockchain.get_latest_block()
            print(f"Blockchain Block Data: {latest_block.data}")
            self.assertEqual(latest_block.data['type'], 'medical_record')
            self.assertTrue(latest_block.data['verified'])
            self.assertIn('signature', latest_block.data)
            self.assertNotEqual(latest_block.data['signature'], 'Simulated Signature')

        # 6. Patient View & Chatbot
        print("--- Testing Patient View & Chatbot ---")
        self.client.get('/logout')
        self.client.post('/login', data={'email': 'patient@test.com', 'password': 'password'}, follow_redirects=True)
        resp = self.client.get('/patient/dashboard')
        self.assertIn(b'Mild Hypertension', resp.data)
        self.assertIn(b'Lisinopril 10mg', resp.data)
        
        # Test Chatbot API
        resp = self.client.post('/api/patient/chat', json={'query': 'What is my diagnosis?'})
        self.assertEqual(resp.status_code, 200)
        # Note: We can't easily verify the AI response content without a real API key, 
        # but we can check if the route handles the request without error.

        # 7. Pharma View
        print("--- Testing Pharma View ---")
        self.client.get('/logout')
        # Register Pharma
        self.client.post('/register', data={
            'email': 'pharma@test.com',
            'password': 'password',
            'name': 'City Pharma',
            'role': 'pharma',
            'organization_name': 'City Pharma Inc'
        }, follow_redirects=True)
        
        self.client.post('/login', data={'email': 'pharma@test.com', 'password': 'password'}, follow_redirects=True)
        resp = self.client.get('/pharma/dashboard')
        self.assertIn(b'Lisinopril 10mg', resp.data)

        print("\n✓ All tests passed successfully!")

if __name__ == '__main__':
    unittest.main()
