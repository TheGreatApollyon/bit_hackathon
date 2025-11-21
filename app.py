"""
HealthCredX - AI Health Analysis + Blockchain Credentials
Multi-user verification platform with document-based authentication
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import os
from pathlib import Path
from werkzeug.utils import secure_filename
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import local modules
import database as db
import auth
import blockchain
import crypto_utils
import ai_verifier
from blockchain import Blockchain

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration
UPLOAD_FOLDER = Path(__file__).parent / 'uploads' / 'documents'
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize blockchain
blockchain = Blockchain()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================================
# PUBLIC ROUTES
# ============================================================

@app.route('/')
def index():
    """Public homepage"""
    user = auth.get_current_user()
    if user:
        # Redirect based on role
        if user['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif user['role'] == 'organization':
            return redirect(url_for('org_dashboard'))
        elif user['role'] == 'practitioner':
            return redirect(url_for('practitioner_dashboard'))
        elif user['role'] == 'hospital':
            return redirect(url_for('hospital_dashboard'))
        elif user['role'] == 'pharma':
            return redirect(url_for('pharma_dashboard'))
        elif user['role'] == 'patient':
            return redirect(url_for('patient_dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = db.get_user_by_email(email)
        
        if user and auth.verify_password(password, user['password']):
            auth.login_user(user)
            flash(f'Welcome back, {user["name"]}!', 'success')
            
            # Redirect based on role
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'organization':
                return redirect(url_for('org_dashboard'))
            elif user['role'] == 'hospital':
                return redirect(url_for('hospital_dashboard'))
            elif user['role'] == 'pharma':
                return redirect(url_for('pharma_dashboard'))
            elif user['role'] == 'patient':
                return redirect(url_for('patient_dashboard'))
            else:
                return redirect(url_for('practitioner_dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        role = request.form.get('role')
        practitioner_type = request.form.get('practitioner_type')
        organization_name = request.form.get('organization_name')
        
        # Hash password
        hashed_password = auth.hash_password(password)
        
        # Create user
        user_id = db.create_user(
            email=email,
            password=hashed_password,
            name=name,
            role=role,
            practitioner_type=practitioner_type if role == 'practitioner' else None,
            organization_name=organization_name if role in ['organization', 'hospital', 'pharma'] else None
        )

        # Generate keys for practitioners
        if role == 'practitioner':
            private_key, public_key = crypto_utils.generate_key_pair()
            db.store_user_keys(user_id, private_key, public_key)
        
        if user_id:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email already exists', 'danger')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout user"""
    auth.logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# ============================================================
# PRACTITIONER ROUTES
# ============================================================

@app.route('/practitioner/dashboard')
@auth.require_role('practitioner')
def practitioner_dashboard():
    """Practitioner dashboard showing verification status and appointments"""
    user = auth.get_current_user()
    verifications = db.get_verifications_by_user(user['id'])
    active_credential = db.get_active_credential(user['id'])
    appointments = db.get_appointments_by_user(user['id'], 'practitioner')
    
    return render_template('practitioner_dashboard.html',
                         verifications=verifications,
                         credential=active_credential,
                         appointments=appointments)

@app.route('/practitioner/visit/<int:appt_id>', methods=['GET', 'POST'])
@auth.require_role('practitioner')
def practitioner_visit(appt_id):
    """Conduct a patient visit"""
    appointment = db.get_appointment_by_id(appt_id)
    if not appointment:
        flash('Appointment not found', 'danger')
        return redirect(url_for('practitioner_dashboard'))
        
    if request.method == 'POST':
        diagnosis = request.form.get('diagnosis')
        prescription = request.form.get('prescription')
        signature = request.form.get('signature') # In real app, this would be a digital signature
        diagnosis_text = request.form.get('diagnosis')
        prescription_text = request.form.get('prescription')
        
        # Create medical record
        record_data = f"{diagnosis_text}|{prescription_text}"
        
        # Get practitioner keys
        keys = db.get_user_keys(session['user_id'])
        signature = "Simulated Signature"
        if keys:
            private_key = keys['private_key']
            signature = crypto_utils.sign_data(private_key, record_data)

        # Add to blockchain (hash of data + signature)
        blockchain_hash = blockchain.add_medical_record({
            "appointment_id": appt_id,
            "diagnosis": diagnosis_text,
            "prescription": prescription_text,
            "signature": signature,
            "doctor_id": session['user_id']
        })
        
        db.create_medical_record(
            appointment_id=appt_id,
            diagnosis_text=diagnosis_text,
            prescription_text=prescription_text,
            doctor_signature=signature,
            blockchain_hash=blockchain_hash
        )
        # Update appointment status
        db.update_appointment_status(appt_id, 'completed')
        
        flash('Visit recorded and secured on blockchain', 'success')
        return redirect(url_for('practitioner_dashboard'))
        
    return render_template('practitioner_visit.html', appointment=appointment)

@app.route('/practitioner/upload', methods=['GET', 'POST'])
@auth.require_role('practitioner')
def upload_documents():
    """Document upload page for practitioners"""
    if request.method == 'POST':
        user = auth.get_current_user()
        
        # Get uploaded files
        files = request.files.getlist('documents')
        document_types = request.form.getlist('document_types')
        
        if not files or len(files) == 0:
            return jsonify({"error": "No files uploaded"}), 400
        
        # Create verification
        verification_id = db.create_verification(user['id'])
        
        # Save documents
        document_ids = []
        for i, file in enumerate(files):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                user_folder = UPLOAD_FOLDER / str(user['id'])
                user_folder.mkdir(exist_ok=True)
                
                filepath = user_folder / f"{verification_id}_{filename}"
                file.save(filepath)
                
                # Store document info
                doc_type = document_types[i] if i < len(document_types) else "Other"
                doc_id = db.create_document(
                    user_id=user['id'],
                    filename=filename,
                    filepath=str(filepath),
                    document_type=doc_type,
                    file_size=os.path.getsize(filepath)
                )
                document_ids.append(doc_id)
                
                # Link to verification
                db.link_document_to_verification(verification_id, doc_id)
        
        # Trigger AI analysis
        db.update_verification_status(verification_id, 'ai_analysis')
        
        return jsonify({
            "success": True,
            "verification_id": verification_id,
            "message": "Documents uploaded successfully. AI analysis will begin shortly."
        })
    
    return render_template('upload_documents.html')

@app.route('/api/analyze-verification/<int:ver_id>', methods=['POST'])
@auth.require_role('practitioner', 'admin')
def analyze_verification(ver_id):
    """Trigger AI analysis for a verification"""
    verification = db.get_verification_by_id(ver_id)
    if not verification:
        return jsonify({"error": "Verification not found"}), 404
    
    # Get documents
    documents = db.get_verification_documents(ver_id)
    
    if not documents:
        return jsonify({"error": "No documents found"}), 400
    
    # Analyze documents
    doc_paths = [(doc['filepath'], doc['document_type']) for doc in documents]
    batch_result = ai_verifier.batch_analyze_documents(doc_paths)
    
    # Update verification with AI results
    db.update_verification_ai_analysis(
        ver_id,
        batch_result['average_score'],
        batch_result
    )
    
    # Update status
    db.update_verification_status(ver_id, 'pending_org')
    
    return jsonify({
        "success": True,
        "score": batch_result['average_score'],
        "analysis": batch_result
    })

# ============================================================
# HOSPITAL ROUTES
# ============================================================

@app.route('/hospital/dashboard')
@auth.require_role('hospital')
def hospital_dashboard():
    """Hospital dashboard"""
    user = auth.get_current_user()
    appointments = db.get_appointments_by_user(user['id'], 'hospital')
    return render_template('hospital_dashboard.html', appointments=appointments)

@app.route('/hospital/onboard-patient', methods=['GET', 'POST'])
@auth.require_role('hospital')
def hospital_onboard_patient():
    """Onboard a new patient"""
    if request.method == 'POST':
        # Create User Account
        email = request.form.get('email')
        password = request.form.get('password') # In real app, generate temp password
        name = request.form.get('name')
        
        # Create Patient Profile
        aadhar = request.form.get('aadhar')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        blood_type = request.form.get('blood_type')
        weight = request.form.get('weight')
        height = request.form.get('height')
        conditions = request.form.get('conditions')
        
        # Hash password
        hashed_password = auth.hash_password(password)
        
        # Create user
        user_id = db.create_user(email, hashed_password, name, 'patient')
        
        if user_id:
            # Create profile
            db.create_patient_profile(user_id, aadhar, dob, gender, blood_type, weight, height, conditions)
            flash('Patient onboarded successfully', 'success')
            return redirect(url_for('hospital_dashboard'))
        else:
            flash('Error creating patient (Email might exist)', 'danger')
            
    return render_template('hospital_onboard_patient.html')

@app.route('/hospital/schedule-appointment', methods=['GET', 'POST'])
@auth.require_role('hospital')
def hospital_schedule_appointment():
    """Schedule an appointment"""
    if request.method == 'POST':
        patient_email = request.form.get('patient_email')
        doctor_email = request.form.get('doctor_email')
        date_time = request.form.get('date_time')
        department = request.form.get('department')
        
        hospital_user = auth.get_current_user()
        
        patient = db.get_user_by_email(patient_email)
        doctor = db.get_user_by_email(doctor_email)
        
        if not patient or patient['role'] != 'patient':
            flash('Invalid patient email', 'danger')
            return redirect(url_for('hospital_schedule_appointment'))
            
        if doctor and doctor['role'] != 'practitioner':
             flash('Invalid doctor email', 'danger')
             return redirect(url_for('hospital_schedule_appointment'))
        
        doctor_id = doctor['id'] if doctor else None
        
        db.create_appointment(patient['id'], doctor_id, hospital_user['id'], date_time, department)
        flash('Appointment scheduled', 'success')
        return redirect(url_for('hospital_dashboard'))
        
    return render_template('hospital_schedule_appointment.html')

# ============================================================
# PATIENT ROUTES
# ============================================================

@app.route('/patient/dashboard')
@auth.require_role('patient')
def patient_dashboard():
    """Patient dashboard"""
    user = auth.get_current_user()
    profile = db.get_patient_profile(user['id'])
    history = db.get_patient_history(user['id'])
    appointments = db.get_appointments_by_user(user['id'], 'patient')
    
    return render_template('patient_dashboard.html', 
                         profile=profile, 
                         history=history,
                         appointments=appointments)

# ============================================================
# PHARMA ROUTES
# ============================================================

@app.route('/pharma/dashboard')
@auth.require_role('pharma')
def pharma_dashboard():
    """Pharma dashboard"""
    prescriptions = db.get_pharma_prescriptions()
    return render_template('pharma_dashboard.html', prescriptions=prescriptions)

@app.route('/pharma/process/<int:record_id>', methods=['POST'])
@auth.require_role('pharma')
def pharma_process_prescription(record_id):
    """Mark prescription as processed"""
    db.update_pharma_status(record_id, 'processed')
    return jsonify({"success": True})

# ============================================================
# ORGANIZATION ROUTES
# ============================================================

@app.route('/organization/dashboard')
@auth.require_role('organization')
def org_dashboard():
    """Organization review dashboard"""
    pending_verifications = db.get_pending_org_verifications()
    return render_template('org_dashboard.html',
                         verifications=pending_verifications)

@app.route('/organization/review/<int:ver_id>')
@auth.require_role('organization')
def org_review_detail(ver_id):
    """Detailed review page for organization"""
    verification = db.get_verification_by_id(ver_id)
    if not verification:
        flash('Verification not found', 'danger')
        return redirect(url_for('org_dashboard'))
    
    documents = db.get_verification_documents(ver_id)
    user_info = db.get_user_by_id(verification['user_id'])
    
    # Parse AI analysis
    ai_analysis = None
    if verification['ai_analysis']:
        ai_analysis = json.loads(verification['ai_analysis'])
    
    return render_template('org_review.html',
                         verification=verification,
                         documents=documents,
                         user_info=user_info,
                         ai_analysis=ai_analysis)

@app.route('/api/organization/submit-review/<int:ver_id>', methods=['POST'])
@auth.require_role('organization')
def org_submit_review(ver_id):
    """Organization submits review verdict"""
    user = auth.get_current_user()
    data = request.json
    
    verdict = data.get('verdict')  # 'approved' or 'rejected'
    comments = data.get('comments', '')
    
    if verdict not in ['approved', 'rejected']:
        return jsonify({"error": "Invalid verdict"}), 400
    
    # Update verification
    db.update_verification_org_review(ver_id, verdict, comments, user['id'])
    
    # If approved by org, move to pending admin
    if verdict == 'approved':
        db.update_verification_status(ver_id, 'pending_admin')
    
    return jsonify({
        "success": True,
        "message": f"Review submitted: {verdict}"
    })

# ============================================================
# ADMIN ROUTES
# ============================================================

@app.route('/admin/dashboard')
@auth.require_role('admin')
def admin_dashboard():
    """Admin control panel"""
    all_verifications = db.get_all_verifications()
    pending_admin = db.get_pending_admin_verifications()
    
    # Check and mark expired credentials
    expired_count = db.check_expired_credentials()
    
    return render_template('admin_dashboard.html',
                         all_verifications=all_verifications,
                         pending_admin=pending_admin,
                         expired_count=expired_count)

@app.route('/admin/review/<int:ver_id>')
@auth.require_role('admin')
def admin_review_detail(ver_id):
    """Admin review detail page"""
    verification = db.get_verification_by_id(ver_id)
    if not verification:
        flash('Verification not found', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    documents = db.get_verification_documents(ver_id)
    user_info = db.get_user_by_id(verification['user_id'])
    
    # Parse AI analysis
    ai_analysis = None
    if verification['ai_analysis']:
        ai_analysis = json.loads(verification['ai_analysis'])
    
    return render_template('admin_review.html',
                         verification=verification,
                         documents=documents,
                         user_info=user_info,
                         ai_analysis=ai_analysis)

@app.route('/api/admin/approve/<int:ver_id>', methods=['POST'])
@auth.require_role('admin')
def admin_approve(ver_id):
    """Admin approves verification and issues credential"""
    user = auth.get_current_user()
    data = request.json
    
    validity_months = data.get('validity_months', 12)  # Default 12 months
    comments = data.get('comments', '')
    
    # Get verification
    verification = db.get_verification_by_id(ver_id)
    if not verification:
        return jsonify({"error": "Verification not found"}), 404
    
    # Update verification with admin approval
    db.update_verification_admin_decision(
        ver_id, 'approved', comments, user['id'], validity_months
    )
    
    # Issue blockchain credential
    user_info = db.get_user_by_id(verification['user_id'])
    credential_hash = blockchain.add_credential(
        user_id=str(verification['user_id']),
        name=user_info['name'],
        skill=user_info.get('practitioner_type', 'Healthcare Professional')
    )
    
    # Create credential record
    db.create_credential(
        verification_id=ver_id,
        user_id=verification['user_id'],
        blockchain_hash=credential_hash,
        validity_months=validity_months
    )
    
    return jsonify({
        "success": True,
        "credential_hash": credential_hash,
        "validity_months": validity_months,
        "message": "Credential approved and issued on blockchain"
    })

@app.route('/api/admin/dismiss/<int:ver_id>', methods=['POST'])
@auth.require_role('admin')
def admin_dismiss(ver_id):
    """Admin dismisses verification"""
    user = auth.get_current_user()
    data = request.json
    
    comments = data.get('comments', 'Dismissed by admin')
    
    # Update verification
    db.update_verification_admin_decision(
        ver_id, 'dismissed', comments, user['id']
    )
    
    return jsonify({
        "success": True,
        "message": "Verification dismissed"
    })

# ============================================================
# API ROUTES
# ============================================================

@app.route('/api/blockchain')
def get_blockchain():
    """Get full blockchain"""
    return jsonify({
        "chain": [block.__dict__ for block in blockchain.chain],
        "length": len(blockchain.chain)
    })

@app.route('/api/verify-credential', methods=['POST'])
def verify_credential():
    """Verify a credential hash on blockchain"""
    data = request.json
    credential_hash = data.get('hash')
    
    is_valid, credential_data = blockchain.verify_credential(credential_hash)
    
    if is_valid:
        return jsonify({
            "verified": True,
            "data": credential_data
        })
    else:
        return jsonify({
            "verified": False,
            "message": "Credential not found on blockchain"
        })

@app.route('/api/document/<int:doc_id>')
@auth.require_login
def serve_document(doc_id):
    """Serve document file (with access control)"""
    user = auth.get_current_user()
    document = db.get_document_by_id(doc_id)
    
    if not document:
        return jsonify({"error": "Document not found"}), 404
    
    # Check permissions
    if user['role'] not in ['admin', 'organization']:
        if document['user_id'] != user['id']:
            return jsonify({"error": "Access denied"}), 403
    
    from flask import send_file
    return send_file(document['filepath'])

# ============================================================
# INITIALIZATION
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("HealthCredX Platform Starting...")
    print("=" * 60)
    
    # Initialize database
    db.init_db()
    
    # Check Gemini API
    if os.environ.get("GEMINI_API_KEY"):
        print("✓ Gemini API configured")
    else:
        print("⚠ Gemini API key not found. Set GEMINI_API_KEY environment variable.")
    
    print(f"✓ Blockchain initialized with {len(blockchain.chain)} block(s)")
    print("=" * 60)
    print("Navigate to: http://127.0.0.1:5000")
    print("=" * 60)
    print("Demo Accounts:")
    print("  Admin: admin@healthcredx.com / admin123")

@app.route('/api/patient/chat', methods=['POST'])
@auth.require_role('patient')
def patient_chat():
    data = request.get_json()
    user_query = data.get('query')
    
    # Get medical history
    history = db.get_medical_records_by_patient(session['user_id'])
    
    # Construct context
    context = "Medical History:\n"
    for record in history:
        context += f"- Date: {record['date_time']}\n"
        context += f"  Doctor: {record['doctor_name']}\n"
        context += f"  Diagnosis: {record['diagnosis_text']}\n"
        context += f"  Prescription: {record['prescription_text']}\n"
    
    # Get AI response
    response = ai_verifier.chat_with_history(context, user_query)
    
    return jsonify({'response': response})
if __name__ == '__main__':
    # Initialize DB
    db.init_db()
    
    print("=" * 60)
    print("HealthCredX Platform Starting...")
    print("=" * 60)
    
    # Initialize Blockchain
    if not blockchain.chain:
        blockchain.create_genesis_block()
    print(f"✓ Blockchain initialized with {len(blockchain.chain)} block(s)")
    
    print("=" * 60)
    print("Navigate to: http://127.0.0.1:5001")
    print("=" * 60)
    print("Demo Accounts:")
    print("  Admin: admin@healthcredx.com / admin123")
    print("  Hospital: hospital@test.com / password")
    print("  Doctor: doctor@test.com / password")
    print("  Patient: patient@test.com / password")
    print("  Pharma: pharma@test.com / password")
    print("=" * 60)
    
    app.run(debug=True, port=5001)
