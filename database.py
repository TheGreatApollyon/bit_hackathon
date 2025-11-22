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
            symptoms TEXT,
            notes TEXT,
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
            delivery_required BOOLEAN DEFAULT 0,
            delivery_address TEXT,
            blockchain_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (appointment_id) REFERENCES appointments(id)
        )
    ''')

    # Inventory table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL, -- tablet, liquid, capsule, injection, etc.
            unit_size TEXT NOT NULL, -- e.g., "500mg", "100ml", "10 tablets"
            stock INTEGER DEFAULT 0,
            price REAL DEFAULT 0.0
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
    seed_comprehensive_data()

def reset_db():
    """Reset database (drop all tables)"""
    conn = get_db()
    cursor = conn.cursor()
    
    tables = ['users', 'documents', 'verifications', 'credentials', 'verification_documents', 
              'patient_profiles', 'appointments', 'user_keys', 'medical_records', 'inventory']
    
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
        
    conn.commit()
    conn.close()
    print("✓ Database reset")
    init_db()

def seed_demo_data():
    """Seed the database with demo accounts"""
    conn = get_db()
    cursor = conn.cursor()
    
    import auth
    import crypto_utils
    hashed_pw = auth.hash_password('password')
    
    # 1. Hospitals
    hospitals = [
        ('hospital@test.com', 'City General Hospital'),
        ('stmarys@test.com', 'St. Mary\'s Medical Center'),
        ('apollo@test.com', 'Apollo Hospitals')
    ]
    
    for email, name in hospitals:
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO users (email, password, name, role, organization_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, hashed_pw, name, 'hospital', name))
            print(f"Seeded {name}")

    # 2. Doctors
    doctors = [
        ('doctor@test.com', 'Dr. Sarah Smith', 'General Physician'),
        ('cardio@test.com', 'Dr. James Wilson', 'Cardiologist'),
        ('ortho@test.com', 'Dr. Emily Chen', 'Orthopedic Surgeon'),
        ('peds@test.com', 'Dr. Michael Brown', 'Pediatrician')
    ]
    
    for email, name, type_ in doctors:
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if not cursor.fetchone():
            private_key, public_key = crypto_utils.generate_key_pair()
            cursor.execute('''
                INSERT INTO users (email, password, name, role, practitioner_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, hashed_pw, name, 'practitioner', type_))
            user_id = cursor.lastrowid
            cursor.execute('INSERT OR REPLACE INTO user_keys (user_id, private_key, public_key) VALUES (?, ?, ?)',
                           (user_id, private_key, public_key))
            print(f"Seeded {name}")

    # 3. Patients
    patients = [
        ('patient@test.com', 'John Doe'),
        ('jane@test.com', 'Jane Smith'),
        ('bob@test.com', 'Bob Johnson')
    ]
    
    for email, name in patients:
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO users (email, password, name, role)
                VALUES (?, ?, ?, ?)
            ''', (email, hashed_pw, name, 'patient'))
            print(f"Seeded {name}")

    # 4. Pharma
    pharmas = [
        ('pharma@test.com', 'MediCare Pharmacy'),
        ('wellness@test.com', 'Wellness Chemist')
    ]
    
    for email, name in pharmas:
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO users (email, password, name, role, organization_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, hashed_pw, name, 'pharma', name))
            print(f"Seeded {name}")
        
    conn.commit()
    conn.close()

def seed_comprehensive_data():
    """Seed database with rich test data"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Only seed if no appointments exist
    cursor.execute("SELECT COUNT(*) as count FROM appointments")
    if cursor.fetchone()['count'] > 0:
        conn.close()
        # Still ensure inventory is seeded
        seed_inventory()
        return

    print("Seeding comprehensive data...")
    
    # Get IDs
    cursor.execute("SELECT id FROM users WHERE email='patient@test.com'")
    patient_id = cursor.fetchone()['id']
    cursor.execute("SELECT id FROM users WHERE email='doctor@test.com'")
    doctor_id = cursor.fetchone()['id']
    cursor.execute("SELECT id FROM users WHERE email='hospital@test.com'")
    hospital_id = cursor.fetchone()['id']

    # Create Patient Profile
    cursor.execute("INSERT OR IGNORE INTO patient_profiles (user_id, aadhar_number, dob, gender, blood_type, weight, height, existing_conditions) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (patient_id, "1234-5678-9012", "1985-06-15", "Male", "O+", 75.5, 178.0, "Asthma, Seasonal Allergies"))

    # Create Past Appointments
    # ... (Keep existing appointment logic but maybe add more if needed, for now keeping it simple to avoid huge file)
    
    # Record 1
    date_1 = (datetime.now() - timedelta(days=180)).isoformat()
    cursor.execute("INSERT INTO appointments (patient_id, doctor_id, hospital_id, date_time, status, department, symptoms) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (patient_id, doctor_id, hospital_id, date_1, 'completed', 'General Medicine', 'Routine checkup'))
    appt_id_1 = cursor.lastrowid
    cursor.execute("INSERT INTO medical_records (appointment_id, diagnosis_text, prescription_text, doctor_signature, blockchain_hash) VALUES (?, ?, ?, ?, ?)",
                   (appt_id_1, "Vitamin D Deficiency", "Vitamin D3 60k IU", "sig_1", "hash_1"))

    conn.commit()
    conn.close()
    seed_inventory()
    print("✓ Comprehensive data seeded")

def seed_inventory():
    """Seed pharmacy inventory with diverse items"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Clear existing to ensure fresh data
    cursor.execute("DELETE FROM inventory")
    
    medicines = [
        # Tablets/Capsules
        ('Amoxicillin', 'tablet', '500mg', 100, 15.50),
        ('Paracetamol', 'tablet', '650mg', 500, 5.00),
        ('Ibuprofen', 'tablet', '400mg', 200, 8.00),
        ('Metformin', 'tablet', '500mg', 300, 12.00),
        ('Atorvastatin', 'tablet', '10mg', 150, 25.00),
        ('Montelukast', 'tablet', '10mg', 100, 18.00),
        ('Azithromycin', 'tablet', '500mg', 80, 35.00),
        ('Pantoprazole', 'tablet', '40mg', 200, 10.00),
        ('Vitamin D3', 'capsule', '60k IU', 50, 45.00),
        ('Omeprazole', 'capsule', '20mg', 150, 12.00),
        
        # Liquids/Syrups
        ('Cough Syrup (Dextromethorphan)', 'liquid', '100ml', 50, 120.00),
        ('Paracetamol Syrup', 'liquid', '60ml', 40, 85.00),
        ('Antacid Liquid', 'liquid', '200ml', 60, 150.00),
        ('Multivitamin Syrup', 'liquid', '200ml', 45, 180.00),
        ('Lactulose Solution', 'liquid', '150ml', 30, 220.00),
        
        # Others
        ('Levosalbutamol Inhaler', 'inhaler', '200 doses', 30, 250.00),
        ('Insulin Glargine', 'injection', '10ml', 20, 500.00),
        ('Diclofenac Gel', 'topical', '30g', 40, 95.00)
    ]
    
    cursor.executemany("INSERT INTO inventory (name, type, unit_size, stock, price) VALUES (?, ?, ?, ?, ?)", medicines)
    conn.commit()
    conn.close()
    print("✓ Inventory seeded with diverse items")

def get_all_medicines():
    """Get all medicines from inventory"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory ORDER BY name")
    items = cursor.fetchall()
    conn.close()
    return [dict(item) for item in items]

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

def get_all_users_safe():
    """Get all users with safe fields (no passwords)"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, email, name, role, practitioner_type, organization_name, 
               created_at, last_login 
        FROM users 
        ORDER BY created_at DESC
    ''')
    users = cursor.fetchall()
    conn.close()
    return [dict(user) for user in users]

def get_dashboard_stats():
    """Get stats for admin dashboard"""
    conn = get_db()
    cursor = conn.cursor()
    
    stats = {}
    
    # Count users by role
    cursor.execute("SELECT role, COUNT(*) as count FROM users GROUP BY role")
    for row in cursor.fetchall():
        stats[f"{row['role']}_count"] = row['count']
        
    # Total patients (fallback if 0 from above)
    if 'patient_count' not in stats: stats['patient_count'] = 0
    if 'hospital_count' not in stats: stats['hospital_count'] = 0
    if 'practitioner_count' not in stats: stats['practitioner_count'] = 0
    
    # Total diagnosis (medical records)
    cursor.execute("SELECT COUNT(*) as count FROM medical_records")
    stats['diagnosis_count'] = cursor.fetchone()['count']
    
    # Pending verifications
    cursor.execute("SELECT COUNT(*) as count FROM verifications WHERE status IN ('pending_org', 'pending_admin')")
    stats['pending_verifications'] = cursor.fetchone()['count']
    
    conn.close()
    return stats

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

def get_practitioner_applications(status=None):
    """Get practitioner applications by status"""
    conn = get_db()
    cursor = conn.cursor()
    
    query = '''
        SELECT v.*, u.name as user_name, u.email as user_email,
               u.practitioner_type, u.organization_name
        FROM verifications v
        JOIN users u ON v.user_id = u.id
        WHERE u.role = 'practitioner'
    '''
    
    if status:
        if status == 'approved':
            query += " AND v.status = 'approved'"
        elif status == 'rejected':
            query += " AND v.status IN ('dismissed', 'org_rejected')"
        elif status == 'pending':
            query += " AND v.status IN ('submitted', 'ai_analysis', 'pending_org', 'pending_admin')"
            
    query += " ORDER BY v.created_at DESC"
    
    cursor.execute(query)
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
def create_medical_record(appointment_id, diagnosis_text, prescription_text, doctor_signature, blockchain_hash, delivery_required=False, delivery_address=None):
    """Create medical record"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO medical_records (appointment_id, diagnosis_text, prescription_text, doctor_signature, blockchain_hash, delivery_required, delivery_address)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (appointment_id, diagnosis_text, prescription_text, doctor_signature, blockchain_hash, delivery_required, delivery_address))
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return record_id

def get_medical_records_by_patient(patient_id):
    """Get all medical records for a patient"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT mr.*, a.date_time, doc.name as doctor_name, hosp.name as hospital_name
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

def get_hospital_stats(hospital_id):
    """Get statistics for hospital dashboard"""
    conn = get_db()
    cursor = conn.cursor()
    
    stats = {}
    
    # Total appointments
    cursor.execute("SELECT COUNT(*) as count FROM appointments WHERE hospital_id = ?", (hospital_id,))
    stats['total_appointments'] = cursor.fetchone()['count']
    
    # Completed appointments
    cursor.execute("SELECT COUNT(*) as count FROM appointments WHERE hospital_id = ? AND status = 'completed'", (hospital_id,))
    stats['completed_appointments'] = cursor.fetchone()['count']
    
    # Scheduled appointments
    cursor.execute("SELECT COUNT(*) as count FROM appointments WHERE hospital_id = ? AND status = 'scheduled'", (hospital_id,))
    stats['scheduled_appointments'] = cursor.fetchone()['count']
    
    # Unique patients
    cursor.execute("SELECT COUNT(DISTINCT patient_id) as count FROM appointments WHERE hospital_id = ?", (hospital_id,))
    stats['total_patients'] = cursor.fetchone()['count']
    
    conn.close()
    return stats

def get_practitioner_stats(user_id):
    """Get statistics for practitioner dashboard"""
    conn = get_db()
    cursor = conn.cursor()
    
    stats = {}
    
    # Total appointments
    cursor.execute("SELECT COUNT(*) as count FROM appointments WHERE doctor_id = ?", (user_id,))
    stats['total_appointments'] = cursor.fetchone()['count']
    
    # Completed appointments
    cursor.execute("SELECT COUNT(*) as count FROM appointments WHERE doctor_id = ? AND status = 'completed'", (user_id,))
    stats['completed_appointments'] = cursor.fetchone()['count']
    
    # Unique patients
    cursor.execute("SELECT COUNT(DISTINCT patient_id) as count FROM appointments WHERE doctor_id = ?", (user_id,))
    stats['total_patients'] = cursor.fetchone()['count']
    
    # Pending appointments
    cursor.execute("SELECT COUNT(*) as count FROM appointments WHERE doctor_id = ? AND status = 'scheduled'", (user_id,))
    stats['pending_appointments'] = cursor.fetchone()['count']
    
    conn.close()
    return stats

def get_patient_stats(user_id):
    """Get statistics for patient dashboard"""
    conn = get_db()
    cursor = conn.cursor()
    
    stats = {}
    
    # Total appointments
    cursor.execute("SELECT COUNT(*) as count FROM appointments WHERE patient_id = ?", (user_id,))
    stats['total_appointments'] = cursor.fetchone()['count']
    
    # Upcoming appointments
    cursor.execute("SELECT COUNT(*) as count FROM appointments WHERE patient_id = ? AND status = 'scheduled'", (user_id,))
    stats['upcoming_appointments'] = cursor.fetchone()['count']
    
    # Completed visits
    cursor.execute("SELECT COUNT(*) as count FROM appointments WHERE patient_id = ? AND status = 'completed'", (user_id,))
    stats['completed_visits'] = cursor.fetchone()['count']
    
    # Total medical records
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM medical_records mr
        JOIN appointments a ON mr.appointment_id = a.id
        WHERE a.patient_id = ?
    """, (user_id,))
    stats['total_records'] = cursor.fetchone()['count']
    
    conn.close()
    return stats

# ============================================================
# AI ASSISTANT SUPPORT FUNCTIONS
# ============================================================

def get_available_doctors(department=None):
    """Get list of available doctors, optionally filtered by department"""
    conn = get_db()
    cursor = conn.cursor()
    
    if department:
        # Try case-insensitive search
        cursor.execute('''
            SELECT id, name, email, practitioner_type 
            FROM users 
            WHERE role = 'practitioner' AND LOWER(practitioner_type) LIKE LOWER(?)
        ''', (f'%{department}%',))
        doctors = cursor.fetchall()
        
        # If no match, return all doctors
        if not doctors:
            cursor.execute('''
                SELECT id, name, email, practitioner_type 
                FROM users 
                WHERE role = 'practitioner'
            ''')
            doctors = cursor.fetchall()
    else:
        cursor.execute('''
            SELECT id, name, email, practitioner_type 
            FROM users 
            WHERE role = 'practitioner'
        ''')
        doctors = cursor.fetchall()
    
    conn.close()
    return [dict(doc) for doc in doctors]

def get_appointment_by_id(appointment_id):
    """Get appointment by ID with full details"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.*, 
               pat.name as patient_name,
               doc.name as doctor_name,
               hosp.name as hospital_name
        FROM appointments a
        LEFT JOIN users pat ON a.patient_id = pat.id
        LEFT JOIN users doc ON a.doctor_id = doc.id
        LEFT JOIN users hosp ON a.hospital_id = hosp.id
        WHERE a.id = ?
    ''', (appointment_id,))
    appt = cursor.fetchone()
    conn.close()
    return dict(appt) if appt else None

def update_appointment_datetime(appointment_id, new_datetime):
    """Update appointment date/time"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE appointments 
        SET date_time = ?
        WHERE id = ?
    ''', (new_datetime, appointment_id))
    conn.commit()
    conn.close()

def update_appointment_status(appointment_id, status):
    """Update appointment status"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE appointments 
        SET status = ?
        WHERE id = ?
    ''', (status, appointment_id))
    conn.commit()
    conn.close()

def get_available_appointment_slots(doctor_id, date):
    """Get available time slots for a doctor on a given date"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get existing appointments for the doctor on that date
    cursor.execute('''
        SELECT date_time 
        FROM appointments 
        WHERE doctor_id = ? AND date(date_time) = date(?) AND status != 'cancelled'
    ''', (doctor_id, date))
    
    booked_slots = [row['date_time'] for row in cursor.fetchall()]
    conn.close()
    
    # Generate available slots (simplified - in real app, would check doctor schedule)
    available_slots = []
    for hour in range(9, 17):  # 9 AM to 5 PM
        slot_time = f"{date} {hour:02d}:00:00"
        if slot_time not in booked_slots:
            available_slots.append(slot_time)
    
    return available_slots

def create_ai_action_log(user_id, action_type, action_data, status='pending'):
    """Log AI-initiated actions for audit trail"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create ai_action_logs table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_action_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action_type TEXT NOT NULL,
            action_data TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        INSERT INTO ai_action_logs (user_id, action_type, action_data, status)
        VALUES (?, ?, ?, ?)
    ''', (user_id, action_type, json.dumps(action_data), status))
    
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()
    return log_id

def update_ai_action_log(log_id, status, completed_at=None):
    """Update AI action log status"""
    conn = get_db()
    cursor = conn.cursor()
    
    if completed_at is None:
        completed_at = datetime.now()
    
    cursor.execute('''
        UPDATE ai_action_logs 
        SET status = ?, completed_at = ?
        WHERE id = ?
    ''', (status, completed_at, log_id))
    
    conn.commit()
    conn.close()

def get_low_stock_items(threshold=20):
    """Get inventory items below stock threshold"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM inventory 
        WHERE stock < ?
        ORDER BY stock ASC
    ''', (threshold,))
    items = cursor.fetchall()
    conn.close()
    return [dict(item) for item in items]

def update_pharma_status(record_id, status):
    """Update pharma processing status"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE medical_records 
        SET pharma_status = ?
        WHERE id = ?
    ''', (status, record_id))
    conn.commit()
    conn.close()

def get_recent_prescriptions(limit=50):
    """Get recent prescriptions for demand forecasting"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT mr.prescription_text, a.date_time
        FROM medical_records mr
        JOIN appointments a ON mr.appointment_id = a.id
        WHERE mr.prescription_text IS NOT NULL AND mr.prescription_text != ''
        ORDER BY a.date_time DESC
        LIMIT ?
    ''', (limit,))
    records = cursor.fetchall()
    conn.close()
    return [dict(rec) for rec in records]

if __name__ == '__main__':
    init_db()
