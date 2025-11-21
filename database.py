"""
Database management for HealthCredX
SQLite database with tables for users, documents, verifications, and credentials
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import json

DB_PATH = Path(__file__).parent / 'data' / 'healthcredx.db'

def get_db():
    """Get database connection"""
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def init_db():
    """Initialize database with schema"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('practitioner', 'organization', 'admin', 'hospital', 'pharma', 'patient')),
            practitioner_type TEXT,
            organization_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Documents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            document_type TEXT NOT NULL,
            file_size INTEGER,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Verifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'submitted' 
                CHECK(status IN ('submitted', 'ai_analysis', 'pending_org', 
                               'org_approved', 'org_rejected', 'pending_admin', 
                               'approved', 'dismissed', 'expired')),
            ai_score INTEGER,
            ai_analysis TEXT,
            org_verdict TEXT,
            org_comments TEXT,
            org_reviewed_by INTEGER,
            org_reviewed_at TIMESTAMP,
            admin_verdict TEXT,
            admin_comments TEXT,
            admin_reviewed_by INTEGER,
            admin_reviewed_at TIMESTAMP,
            validity_months INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (org_reviewed_by) REFERENCES users(id),
            FOREIGN KEY (admin_reviewed_by) REFERENCES users(id)
        )
    ''')
    
    # Credentials table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            verification_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            blockchain_hash TEXT,
            issued_at TIMESTAMP,
            expires_at TIMESTAMP,
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'expired', 'revoked')),
            FOREIGN KEY (verification_id) REFERENCES verifications(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Document-Verification link table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verification_documents (
            verification_id INTEGER NOT NULL,
            document_id INTEGER NOT NULL,
            PRIMARY KEY (verification_id, document_id),
            FOREIGN KEY (verification_id) REFERENCES verifications(id),
            FOREIGN KEY (document_id) REFERENCES documents(id)
        )

    ''')

    # Patient Profiles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patient_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            aadhar_number TEXT UNIQUE,
            dob DATE,
            gender TEXT,
            blood_type TEXT,
            weight REAL,
            height REAL,
            existing_conditions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Appointments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER,
            hospital_id INTEGER NOT NULL,
            date_time TIMESTAMP NOT NULL,
            department TEXT,
            status TEXT DEFAULT 'scheduled' CHECK(status IN ('scheduled', 'completed', 'cancelled')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES users(id),
            FOREIGN KEY (doctor_id) REFERENCES users(id),
            FOREIGN KEY (hospital_id) REFERENCES users(id)
        )
    ''')

    # User Keys table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_keys (
            user_id INTEGER PRIMARY KEY,
            public_key TEXT NOT NULL,
            private_key TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Medical Records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medical_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER NOT NULL,
            diagnosis_text TEXT NOT NULL,
            prescription_text TEXT,
            doctor_signature TEXT,
            pharma_status TEXT DEFAULT 'pending',
            blockchain_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (appointment_id) REFERENCES appointments(id)
        )
    ''')
    
    conn.commit()
    
    # Create default admin if not exists
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE role='admin'")
    if cursor.fetchone()['count'] == 0:
        cursor.execute('''
            INSERT INTO users (email, password, name, role)
            VALUES (?, ?, ?, ?)
        ''', ('admin@healthcredx.com', 'admin123', 'System Admin', 'admin'))
        conn.commit()
        print("✓ Default admin created (admin@healthcredx.com / admin123)")
    
    conn.close()
    
    # Seed demo data
    seed_demo_data()

def seed_demo_data():
    """Seed the database with demo accounts if they don't exist"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Hospital
    cursor.execute('SELECT id FROM users WHERE email = ?', ('hospital@test.com',))
    if not cursor.fetchone():
        import auth
        hashed_pw = auth.hash_password('password')
        cursor.execute('''
            INSERT INTO users (email, password, name, role, organization_name)
            VALUES (?, ?, ?, ?, ?)
        ''', ('hospital@test.com', hashed_pw, 'City General Hospital', 'hospital', 'City General Hospital'))
        print("Seeded Hospital account")

    # 2. Doctor
    cursor.execute('SELECT id FROM users WHERE email = ?', ('doctor@test.com',))
    if not cursor.fetchone():
        import auth
        hashed_pw = auth.hash_password('password')
        # Generate keys for doctor
        import crypto_utils
        private_key, public_key = crypto_utils.generate_key_pair()
        
        cursor.execute('''
            INSERT INTO users (email, password, name, role, practitioner_type)
            VALUES (?, ?, ?, ?, ?)
        ''', ('doctor@test.com', hashed_pw, 'Dr. Sarah Smith', 'practitioner', 'Doctor'))
        user_id = cursor.lastrowid
        
        # Store keys using SAME cursor to avoid locking
        cursor.execute('INSERT OR REPLACE INTO user_keys (user_id, private_key, public_key) VALUES (?, ?, ?)',
                       (user_id, private_key, public_key))
        print("Seeded Doctor account with keys")

    # 3. Patient
    cursor.execute('SELECT id FROM users WHERE email = ?', ('patient@test.com',))
    if not cursor.fetchone():
        import auth
        hashed_pw = auth.hash_password('password')
        cursor.execute('''
            INSERT INTO users (email, password, name, role)
            VALUES (?, ?, ?, ?)
        ''', ('patient@test.com', hashed_pw, 'John Doe', 'patient'))
        print("Seeded Patient account")

    # 4. Pharma
    cursor.execute('SELECT id FROM users WHERE email = ?', ('pharma@test.com',))
    if not cursor.fetchone():
        import auth
        hashed_pw = auth.hash_password('password')
        cursor.execute('''
            INSERT INTO users (email, password, name, role, organization_name)
            VALUES (?, ?, ?, ?, ?)
        ''', ('pharma@test.com', hashed_pw, 'MediCare Pharmacy', 'pharma', 'MediCare Pharmacy'))
        print("Seeded Pharma account")
        
    conn.commit()
    conn.close()
    print("✓ Database initialized")

# User operations
def create_user(email, password, name, role, practitioner_type=None, organization_name=None):
    """Create a new user"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (email, password, name, role, practitioner_type, organization_name)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (email, password, name, role, practitioner_type, organization_name))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def get_user_by_email(email):
    """Get user by email"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def update_last_login(user_id):
    """Update user's last login time"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                   (datetime.now(), user_id))
    conn.commit()
    conn.close()

# Document operations
def create_document(user_id, filename, filepath, document_type, file_size):
    """Create document record"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO documents (user_id, filename, filepath, document_type, file_size)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, filename, filepath, document_type, file_size))
    conn.commit()
    doc_id = cursor.lastrowid
    conn.close()
    return doc_id

def get_documents_by_user(user_id):
    """Get all documents for a user"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM documents WHERE user_id = ? ORDER BY upload_date DESC', 
                   (user_id,))
    docs = cursor.fetchall()
    conn.close()
    return [dict(doc) for doc in docs]

def get_document_by_id(doc_id):
    """Get document by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
    doc = cursor.fetchone()
    conn.close()
    return dict(doc) if doc else None

# Verification operations
def create_verification(user_id):
    """Create new verification request"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO verifications (user_id, status)
        VALUES (?, 'submitted')
    ''', (user_id,))
    conn.commit()
    ver_id = cursor.lastrowid
    conn.close()
    return ver_id

def link_document_to_verification(verification_id, document_id):
    """Link a document to a verification"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO verification_documents (verification_id, document_id)
        VALUES (?, ?)
    ''', (verification_id, document_id))
    conn.commit()
    conn.close()

def update_verification_status(ver_id, status):
    """Update verification status"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE verifications 
        SET status = ?, updated_at = ?
        WHERE id = ?
    ''', (status, datetime.now(), ver_id))
    conn.commit()
    conn.close()

def update_verification_ai_analysis(ver_id, score, analysis):
    """Update verification with AI analysis results"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE verifications 
        SET ai_score = ?, ai_analysis = ?, status = 'pending_org', updated_at = ?
        WHERE id = ?
    ''', (score, json.dumps(analysis), datetime.now(), ver_id))
    conn.commit()
    conn.close()

def update_verification_org_review(ver_id, verdict, comments, reviewer_id):
    """Update verification with organization review"""
    conn = get_db()
    cursor = conn.cursor()
    new_status = 'org_approved' if verdict == 'approved' else 'org_rejected'
    cursor.execute('''
        UPDATE verifications 
        SET org_verdict = ?, org_comments = ?, org_reviewed_by = ?, 
            org_reviewed_at = ?, status = ?, updated_at = ?
        WHERE id = ?
    ''', (verdict, comments, reviewer_id, datetime.now(), new_status, datetime.now(), ver_id))
    conn.commit()
    conn.close()

def update_verification_admin_decision(ver_id, verdict, comments, admin_id, validity_months=None):
    """Update verification with admin decision"""
    conn = get_db()
    cursor = conn.cursor()
    new_status = 'approved' if verdict == 'approved' else 'dismissed'
    cursor.execute('''
        UPDATE verifications 
        SET admin_verdict = ?, admin_comments = ?, admin_reviewed_by = ?,
            admin_reviewed_at = ?, validity_months = ?, status = ?, updated_at = ?
        WHERE id = ?
    ''', (verdict, comments, admin_id, datetime.now(), validity_months, new_status, datetime.now(), ver_id))
    conn.commit()
    conn.close()

def get_verification_by_id(ver_id):
    """Get verification by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM verifications WHERE id = ?', (ver_id,))
    ver = cursor.fetchone()
    conn.close()
    return dict(ver) if ver else None

def get_verifications_by_user(user_id):
    """Get all verifications for a user"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM verifications 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (user_id,))
    vers = cursor.fetchall()
    conn.close()
    return [dict(ver) for ver in vers]

def get_pending_org_verifications():
    """Get all verifications pending organization review"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.*, u.name as user_name, u.email as user_email, 
               u.practitioner_type
        FROM verifications v
        JOIN users u ON v.user_id = u.id
        WHERE v.status = 'pending_org'
        ORDER BY v.created_at ASC
    ''')
    vers = cursor.fetchall()
    conn.close()
    return [dict(ver) for ver in vers]

def get_pending_admin_verifications():
    """Get all verifications pending admin approval"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.*, u.name as user_name, u.email as user_email,
               u.practitioner_type
        FROM verifications v
        JOIN users u ON v.user_id = u.id
        WHERE v.status = 'pending_admin'
        ORDER BY v.created_at ASC
    ''')
    vers = cursor.fetchall()
    conn.close()
    return [dict(ver) for ver in vers]

def get_all_verifications():
    """Get all verifications (for admin)"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.*, u.name as user_name, u.email as user_email,
               u.practitioner_type
        FROM verifications v
        JOIN users u ON v.user_id = u.id
        ORDER BY v.created_at DESC
    ''')
    vers = cursor.fetchall()
    conn.close()
    return [dict(ver) for ver in vers]

def get_verification_documents(ver_id):
    """Get all documents for a verification"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT d.*
        FROM documents d
        JOIN verification_documents vd ON d.id = vd.document_id
        WHERE vd.verification_id = ?
    ''', (ver_id,))
    docs = cursor.fetchall()
    conn.close()
    return [dict(doc) for doc in docs]

# Credential operations
def create_credential(verification_id, user_id, blockchain_hash, validity_months):
    """Create credential after approval"""
    conn = get_db()
    cursor = conn.cursor()
    issued_at = datetime.now()
    expires_at = issued_at + timedelta(days=30 * validity_months)
    
    cursor.execute('''
        INSERT INTO credentials (verification_id, user_id, blockchain_hash, 
                                issued_at, expires_at, status)
        VALUES (?, ?, ?, ?, ?, 'active')
    ''', (verification_id, user_id, blockchain_hash, issued_at, expires_at))
    conn.commit()
    cred_id = cursor.lastrowid
    conn.close()
    return cred_id

def get_active_credential(user_id):
    """Get active credential for a user"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM credentials 
        WHERE user_id = ? AND status = 'active'
        ORDER BY issued_at DESC
        LIMIT 1
    ''', (user_id,))
    cred = cursor.fetchone()
    conn.close()
    return dict(cred) if cred else None

def check_expired_credentials():
    """Mark expired credentials"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE credentials 
        SET status = 'expired'
        WHERE status = 'active' AND expires_at < ?
    ''', (datetime.now(),))
    conn.commit()
    expired_count = cursor.rowcount
    conn.close()
    return expired_count

# Patient operations
def create_patient_profile(user_id, aadhar_number, dob, gender, blood_type, weight, height, existing_conditions):
    """Create patient profile"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO patient_profiles (user_id, aadhar_number, dob, gender, blood_type, weight, height, existing_conditions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, aadhar_number, dob, gender, blood_type, weight, height, existing_conditions))
        conn.commit()
        profile_id = cursor.lastrowid
        conn.close()
        return profile_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def get_patient_profile(user_id):
    """Get patient profile by user_id"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM patient_profiles WHERE user_id = ?', (user_id,))
    profile = cursor.fetchone()
    conn.close()
    return dict(profile) if profile else None

# Appointment operations
def create_appointment(patient_id, doctor_id, hospital_id, date_time, department):
    """Create new appointment"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO appointments (patient_id, doctor_id, hospital_id, date_time, department)
        VALUES (?, ?, ?, ?, ?)
    ''', (patient_id, doctor_id, hospital_id, date_time, department))
    conn.commit()
    appt_id = cursor.lastrowid
    conn.close()
    return appt_id

def get_appointments_by_user(user_id, role):
    """Get appointments for a user based on role"""
    conn = get_db()
    cursor = conn.cursor()
    
    if role == 'patient':
        query = '''
            SELECT a.*, 
                   doc.name as doctor_name, 
                   hosp.name as hospital_name,
                   hosp.organization_name as hospital_org_name
            FROM appointments a
            LEFT JOIN users doc ON a.doctor_id = doc.id
            JOIN users hosp ON a.hospital_id = hosp.id
            WHERE a.patient_id = ?
            ORDER BY a.date_time DESC
        '''
    elif role == 'practitioner':
        query = '''
            SELECT a.*, 
                   pat.name as patient_name,
                   prof.aadhar_number,
                   prof.gender,
                   prof.dob
            FROM appointments a
            JOIN users pat ON a.patient_id = pat.id
            LEFT JOIN patient_profiles prof ON pat.id = prof.user_id
            WHERE a.doctor_id = ?
            ORDER BY a.date_time ASC
        '''
    elif role == 'hospital':
        query = '''
            SELECT a.*, 
                   pat.name as patient_name,
                   doc.name as doctor_name
            FROM appointments a
            JOIN users pat ON a.patient_id = pat.id
            LEFT JOIN users doc ON a.doctor_id = doc.id
            WHERE a.hospital_id = ?
            ORDER BY a.date_time ASC
        '''
    else:
        return []

    cursor.execute(query, (user_id,))
    appts = cursor.fetchall()
    conn.close()
    return [dict(appt) for appt in appts]

def get_appointment_by_id(appt_id):
    """Get appointment by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.*, 
               pat.name as patient_name,
               pat.email as patient_email,
               prof.aadhar_number,
               prof.gender,
               prof.dob,
               prof.blood_type,
               prof.weight,
               prof.height,
               prof.existing_conditions
        FROM appointments a
        JOIN users pat ON a.patient_id = pat.id
        LEFT JOIN patient_profiles prof ON pat.id = prof.user_id
        WHERE a.id = ?
    ''', (appt_id,))
    appt = cursor.fetchone()
    conn.close()
    return dict(appt) if appt else None

def update_appointment_status(appt_id, status):
    """Update appointment status"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE appointments SET status = ? WHERE id = ?', (status, appt_id))
    conn.commit()
    conn.close()

# Medical Record operations
def create_medical_record(appointment_id, diagnosis_text, prescription_text, doctor_signature, blockchain_hash):
    """Create medical record"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO medical_records (appointment_id, diagnosis_text, prescription_text, doctor_signature, blockchain_hash)
        VALUES (?, ?, ?, ?, ?)
    ''', (appointment_id, diagnosis_text, prescription_text, doctor_signature, blockchain_hash))
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return record_id

def store_user_keys(user_id, private_key, public_key):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO user_keys (user_id, private_key, public_key) VALUES (?, ?, ?)',
                   (user_id, private_key, public_key))
    conn.commit()
    conn.close()

def get_user_keys(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT private_key, public_key FROM user_keys WHERE user_id = ?', (user_id,))
    keys = cursor.fetchone()
    conn.close()
    return keys

def get_medical_record_by_appointment(appointment_id):
    """Get medical record for an appointment"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM medical_records WHERE appointment_id = ?', (appointment_id,))
    record = cursor.fetchone()
    conn.close()
    return dict(record) if record else None

def get_patient_history(patient_id):
    """Get full medical history for a patient"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT mr.*, 
               a.date_time, 
               a.department,
               doc.name as doctor_name,
               hosp.name as hospital_name
        FROM medical_records mr
        JOIN appointments a ON mr.appointment_id = a.id
        JOIN users doc ON a.doctor_id = doc.id
        JOIN users hosp ON a.hospital_id = hosp.id
        WHERE a.patient_id = ?
        ORDER BY a.date_time DESC
    ''', (patient_id,))
    records = cursor.fetchall()
    conn.close()
    return [dict(rec) for rec in records]

def get_pharma_prescriptions():
    """Get all prescriptions for pharma to process"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT mr.*, 
               pat.name as patient_name,
               doc.name as doctor_name,
               a.date_time
        FROM medical_records mr
        JOIN appointments a ON mr.appointment_id = a.id
        JOIN users pat ON a.patient_id = pat.id
        JOIN users doc ON a.doctor_id = doc.id
        WHERE mr.prescription_text IS NOT NULL AND mr.prescription_text != ''
        ORDER BY a.date_time DESC
    ''')
    records = cursor.fetchall()
    conn.close()
    return [dict(rec) for rec in records]

def get_medical_records_by_patient(patient_id):
    """Get all medical records for a patient"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT mr.*, a.date_time, u.name as doctor_name
        FROM medical_records mr
        JOIN appointments a ON mr.appointment_id = a.id
        JOIN users u ON a.doctor_id = u.id
        WHERE a.patient_id = ?
        ORDER BY a.date_time DESC
    ''', (patient_id,))
    records = cursor.fetchall()
    conn.close()
    return [dict(row) for row in records]

if __name__ == '__main__':
    init_db()
