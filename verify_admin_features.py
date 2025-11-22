import unittest
import os
import tempfile
from app import app, db
import database
import json

class AdminFeaturesTest(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['DATABASE'] = self.db_path
        
        from pathlib import Path
        database.DB_PATH = Path(self.db_path)
        
        self.client = app.test_client()
        with app.app_context():
            database.init_db()
            
            # Create test data
            # 1. Create Admin
            # (Already created by init_db)
            
            # 2. Create Practitioner
            self.practitioner_id = database.create_user('doc@test.com', 'pass', 'Dr. Test', 'practitioner', 'Cardio')
            
            # 3. Create Verification
            self.ver_id = database.create_verification(self.practitioner_id)
            database.update_verification_status(self.ver_id, 'pending_admin')
            database.update_verification_ai_analysis(self.ver_id, 85, {"score": 85})

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def login_admin(self):
        return self.client.post('/login', data={
            'email': 'admin@healthcredx.com',
            'password': 'admin123'
        }, follow_redirects=True)

    def test_admin_dashboard_stats(self):
        self.login_admin()
        resp = self.client.get('/admin/dashboard')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Dashboard Overview', resp.data)
        self.assertIn(b'Total Patients', resp.data)
        # Check if stats are rendered (e.g., "1" for pending verifications)
        self.assertIn(b'1', resp.data) 

    def test_practitioner_applications(self):
        self.login_admin()
        
        # Test Pending Tab
        resp = self.client.get('/admin/applications?status=pending')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Dr. Test', resp.data)
        
        # Test Approved Tab (should be empty)
        resp = self.client.get('/admin/applications?status=approved')
        self.assertNotIn(b'Dr. Test', resp.data)

    def test_manage_users(self):
        self.login_admin()
        resp = self.client.get('/admin/users')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'User Management', resp.data)
        self.assertIn(b'doc@test.com', resp.data)
        # Ensure password is NOT shown (basic check)
        self.assertNotIn(b'pass', resp.data)

    def test_admin_chatbot(self):
        self.login_admin()
        # Mocking the AI response would be ideal, but for integration test we check if route exists and handles request
        # We expect it might fail if no API key, but it should return a JSON response
        resp = self.client.post('/api/admin/chat', json={'query': 'How many patients?'})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertIn('response', data)

if __name__ == '__main__':
    unittest.main()
