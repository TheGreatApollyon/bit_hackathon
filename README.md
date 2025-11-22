# 🏥 HealthCredX

> **AI-Powered Healthcare Management Platform with Blockchain Credential Verification**
Live demo: https://bit-hackathon-v3ma.onrender.com/

HealthCredX is a comprehensive healthcare management platform that revolutionizes medical credential verification, patient care coordination, and prescription management using cutting-edge AI and blockchain technology.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![Gemini AI](https://img.shields.io/badge/Gemini-2.5%20Flash-orange.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 Key Features

### 🔐 **AI-Powered Document Verification**
- **Intelligent Document Analysis**: Leverages Google Gemini 2.5 Flash to analyze medical credentials, certificates, and licenses
- **Multi-Stage Verification**: Three-tier verification process (AI → Educational Organization → Admin)
- **Authenticity Scoring**: Advanced AI scoring system with detailed analysis reports
- **Document Security**: Secure document storage with role-based access control

### 🔗 **Blockchain Credential Management**
- **Immutable Credentials**: Medical credentials and records stored on a custom blockchain
- **Cryptographic Signatures**: Digital signing of medical records using public-key cryptography
- **Tamper-Proof Records**: Ensures data integrity and prevents credential fraud
- **Real-Time Verification**: Instant credential verification via blockchain hash lookup

### 🤖 **AI Medical Assistant**
- **RAG-Powered Chatbot**: Context-aware medical history chatbot for patients
- **Function Calling**: Intelligent appointment scheduling via natural language
- **Medical History Analysis**: AI provides insights based on patient's medical records
- **Dashboard Analytics**: Admin chatbot for data-driven insights and statistics

### 👥 **Multi-Role Platform**
HealthCredX supports six distinct user roles, each with specialized dashboards:

#### 🏥 **Hospitals**
- Patient onboarding and profile management
- Appointment scheduling system
- Department-wise organization
- Statistics and analytics dashboard

#### 👨‍⚕️ **Medical Practitioners**
- Credential verification workflow
- Patient consultation interface
- Handwriting recognition for prescriptions
- Digital prescription management with intelligent medicine calculations
- Medical record blockchain integration

#### 👤 **Patients**
- Comprehensive medical history dashboard
- AI chatbot for medical queries and appointment booking
- Prescription tracking and pharmacy delivery
- Secure access to all medical records

#### 💊 **Pharmacies**
- Prescription processing dashboard
- Medicine inventory management
- Smart dosage calculations (tablets, liquids, injections, etc.)
- Delivery coordination

#### 🏛️ **Educational Organizations**
- Review practitioner credential applications
- Verify educational certificates
- Approve/reject verification requests

#### 🛡️ **Administrators**
- System-wide oversight and control
- Final credential approval authority
- User management dashboard
- RAG chatbot for administrative insights
- Expired credential monitoring

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend Layer                          │
│        (HTML/CSS/JavaScript + Material Web)                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Flask Application Layer                    │
│  • Route Handlers  • Auth Middleware  • Session Management   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────┬──────────────┬──────────────┬───────────────┐
│   Database   │  AI Services │  Blockchain  │    Crypto     │
│   (SQLite)   │   (Gemini)   │   (Custom)   │  (RSA/SHA)    │
└──────────────┴──────────────┴──────────────┴───────────────┘
```

### Core Components

- **`app.py`** - Main Flask application with all routes and business logic
- **`database.py`** - SQLite database operations and data models
- **`auth.py`** - Authentication and authorization middleware
- **`ai_verifier.py`** - Gemini AI integration for document verification
- **`ai_assistant.py`** - RAG chatbot and function calling implementation
- **`blockchain.py`** - Custom blockchain for credential storage
- **`crypto_utils.py`** - Cryptographic utilities (RSA, SHA-256)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/healthcredx.git
cd healthcredx
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Update the .env file with your API key
# Edit .env and ensure GEMINI_API_KEY is set
```

5. **Initialize the database**
```bash
python init_db.py
```

6. **Run the application**
```bash
python app.py
```

The application will be available at `http://localhost:5000`

---

## 🔑 Test Accounts

The platform comes pre-seeded with test accounts for all roles:

| Role | Email | Password | Description |
|------|-------|----------|-------------|
| **Admin** | admin@healthcredx.com | password | System administrator |
| **Hospital** | hospital@test.com | password | City General Hospital |
| **Hospital** | stmarys@test.com | password | St. Mary's Medical Center |
| **Hospital** | apollo@test.com | password | Apollo Hospitals |
| **Practitioner** | doctor@test.com | password | Dr. Sarah Smith (General Physician) |
| **Practitioner** | cardio@test.com | password | Dr. James Wilson (Cardiologist) |
| **Practitioner** | ortho@test.com | password | Dr. Emily Chen (Orthopedic Surgeon) |
| **Practitioner** | peds@test.com | password | Dr. Michael Brown (Pediatrician) |
| **Patient** | patient@test.com | password | John Doe |
| **Patient** | jane@test.com | password | Jane Smith |
| **Patient** | bob@test.com | password | Bob Johnson |
| **Pharmacy** | pharma@test.com | password | MediCare Pharmacy |
| **Pharmacy** | wellness@test.com | password | Wellness Chemist |

---

## 📋 Detailed Features

### Practitioner Verification Workflow

1. **Document Upload**: Practitioners upload medical certificates, licenses, and credentials
2. **AI Analysis**: Gemini AI analyzes documents for authenticity (scoring 0-100)
3. **Organization Review**: Educational institutions verify the credentials
4. **Admin Approval**: System admin provides final approval
5. **Blockchain Issuance**: Verified credentials are stored on the blockchain
6. **Credential Expiry**: Automatic tracking of credential expiration (configurable validity)

### Smart Prescription System

- **Handwriting Recognition**: AI-powered OCR for handwritten prescriptions
- **Medicine Database**: Comprehensive inventory of medicines with types (tablets, liquids, capsules, injections, etc.)
- **Intelligent Calculations**: 
  - Automatic tablet count calculation based on dosage and duration
  - Liquid medicine bottle calculations (e.g., syrups)
  - Frequency and timing management (morning, afternoon, evening, night)
- **Digital Signatures**: Cryptographically signed prescriptions for authenticity
- **Blockchain Recording**: All prescriptions stored immutably on blockchain

### AI Chatbot Features

#### Patient Chatbot
- **Medical History Context**: Access to complete medical history for relevant responses
- **Appointment Booking**: Natural language appointment scheduling
  - "Book me an appointment with a cardiologist next week"
  - Automatic doctor and hospital assignment
- **Medical Queries**: Answer questions about past diagnoses and treatments

#### Admin Chatbot
- **Dashboard Analytics**: Query system statistics and metrics
- **Application Insights**: Get summaries of pending verifications
- **Data-Driven Decisions**: AI-powered recommendations based on platform data

---

## 🗄️ Database Schema

### Core Tables

- **users** - All platform users with role-based access
- **patient_profiles** - Extended patient information (Aadhar, blood type, conditions, etc.)
- **documents** - Uploaded medical certificates and credentials
- **verifications** - Credential verification requests and workflow state
- **credentials** - Blockchain-backed verified credentials
- **appointments** - Hospital appointments and scheduling
- **medical_records** - Patient diagnoses, prescriptions, and signatures
- **inventory** - Pharmacy medicine inventory
- **user_keys** - RSA key pairs for digital signatures

---

## 🔐 Security Features

- **Password Hashing**: Bcrypt-based secure password storage
- **Session Management**: Flask session-based authentication
- **Role-Based Access Control**: Decorator-based authorization (@require_role)
- **Document Access Control**: Users can only access their own documents (except admins/orgs)
- **Digital Signatures**: RSA-2048 signatures for medical records
- **Blockchain Integrity**: SHA-256 hashing for tamper-proof records
- **File Upload Validation**: Size limits and allowed file type restrictions

---

## 🤖 AI Integration

### Document Verification (Gemini 2.5 Flash)

```python
# Analyzes uploaded documents and provides:
{
  "average_score": 92,
  "documents": [
    {
      "type": "Medical Degree",
      "score": 95,
      "analysis": "Authentic certificate from recognized institution...",
      "flags": []
    }
  ],
  "overall_verdict": "Documents appear authentic"
}
```

### RAG Chatbot

- **Patient Context**: Retrieves relevant medical history before generating responses
- **Function Calling**: Executes actions like appointment scheduling
- **Contextual Understanding**: Maintains conversation context for multi-turn interactions

---

## 🧪 Testing

### Comprehensive Test Suite

```bash
# Test AI document verification
python demo_ai_verification.py

# Test AI chatbot and function calling
python test_ai_features_comprehensive.py

# Test database expansion
python test_expansion.py

# Verify admin features
python verify_admin_features.py
```

---

## 📁 Project Structure

```
healthcredx/
├── app.py                          # Main Flask application
├── database.py                     # Database operations
├── auth.py                         # Authentication middleware
├── ai_verifier.py                  # Gemini AI document verification
├── ai_assistant.py                 # RAG chatbot implementation
├── blockchain.py                   # Custom blockchain
├── crypto_utils.py                 # Cryptographic utilities
├── init_db.py                      # Database initialization
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables
├── data/
│   └── healthcredx.db             # SQLite database
├── uploads/
│   └── documents/                 # User uploaded files
├── templates/                      # HTML templates
│   ├── index.html
│   ├── login.html
│   ├── practitioner_dashboard.html
│   ├── patient_dashboard.html
│   ├── admin_dashboard.html
│   └── ... (18 templates total)
├── smart_contracts/               # Blockchain smart contracts
└── README.md                      # This file
```

---

## 🌐 API Endpoints

### Public Endpoints
- `GET /` - Homepage
- `POST /login` - User authentication
- `GET /logout` - User logout

### Practitioner Endpoints
- `GET /practitioner/dashboard` - Main dashboard
- `POST /practitioner/upload` - Upload credentials
- `POST /practitioner/visit/<id>` - Conduct patient visit
- `POST /api/practitioner/analyze-handwriting` - OCR for prescriptions
- `GET /api/medicines` - Get medicine inventory

### Patient Endpoints
- `GET /patient/dashboard` - Patient dashboard with history
- `POST /api/patient/chat` - AI chatbot for medical queries
- `POST /api/patient/ai-assistant` - AI assistant with function calling

### Hospital Endpoints
- `GET /hospital/dashboard` - Hospital dashboard
- `POST /hospital/onboard-patient` - Register new patient
- `POST /hospital/schedule-appointment` - Schedule appointment

### Pharmacy Endpoints
- `GET /pharma/dashboard` - View prescriptions
- `POST /pharma/process/<id>` - Mark prescription as processed

### Organization Endpoints
- `GET /organization/dashboard` - View pending verifications
- `POST /api/organization/submit-review/<id>` - Submit verdict

### Admin Endpoints
- `GET /admin/dashboard` - System overview
- `GET /admin/applications` - Practitioner applications
- `GET /admin/users` - User management
- `POST /api/admin/approve/<id>` - Approve credential
- `POST /api/admin/chat` - RAG chatbot for analytics

### API Endpoints
- `GET /api/blockchain` - View full blockchain
- `POST /api/verify-credential` - Verify credential hash
- `POST /api/analyze-verification/<id>` - Trigger AI analysis

---

## 🎨 Tech Stack

### Backend
- **Flask 3.0.0** - Web framework
- **SQLite** - Database
- **Python-dotenv** - Environment management

### AI & ML
- **Google Generative AI (Gemini 2.5 Flash)** - Document verification and chatbots
- **Pillow** - Image processing for handwriting recognition

### Security
- **Cryptography 41.0.0** - RSA encryption and signatures
- **SHA-256** - Blockchain hashing

### Frontend
- **HTML5 + CSS3** - Structure and styling
- **Vanilla JavaScript** - Interactivity
- **Material Web Components** - Modern UI components
- **Responsive Design** - Mobile-friendly interface

---

## 🔄 Blockchain Implementation

### Block Structure
```python
{
  "index": 1,
  "timestamp": "2025-11-22 12:00:00",
  "data": {
    "user_id": "123",
    "name": "Dr. John Doe",
    "credential_type": "Medical License",
    "validity": "2026-11-22"
  },
  "previous_hash": "0000abc...",
  "hash": "0000def...",
  "nonce": 12345
}
```

### Features
- **Proof of Work**: Mining algorithm for block validation
- **Chain Validation**: Ensures no tampering with historical records
- **Credential Storage**: Medical credentials and records
- **Hash-based Verification**: Quick credential lookup and verification

---

## 📊 Key Metrics & Analytics

The admin dashboard provides:
- Total users by role (patients, practitioners, hospitals, etc.)
- Total diagnoses/medical records
- Pending verifications count
- Expired credentials monitoring
- Application status tracking

---

## 🛠️ Development

### Running in Development Mode

```bash
# Enable Flask debug mode
export FLASK_ENV=development  # On Windows: set FLASK_ENV=development
python app.py
```

### Database Management

```bash
# Initialize fresh database
python init_db.py

# Reset database (CAUTION: Deletes all data)
python -c "from database import reset_db; reset_db()"
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Gemini AI** - For powerful document verification and chatbot capabilities
- **Material Design** - For beautiful UI components
- **Flask Community** - For excellent documentation and support

---

## 📞 Support

For support, email support@healthcredx.com or open an issue in the GitHub repository.

---

## 🚧 Roadmap

- [ ] Multi-language support
- [ ] Mobile app development (iOS/Android)
- [ ] Integration with national health databases
- [ ] Video consultation feature
- [ ] Real-time notifications
- [ ] Advanced analytics and reporting
- [ ] Multi-hospital network support
- [ ] Insurance integration
- [ ] Telemedicine capabilities

---

## ⚠️ Disclaimer

This is a demonstration/hackathon project. For production use:
- Use a production-grade database (PostgreSQL/MySQL)
- Implement proper API rate limiting
- Add comprehensive error handling
- Use environment-specific configurations
- Implement proper backup strategies
- Add comprehensive logging and monitoring
- Conduct security audits
- Comply with healthcare regulations (HIPAA, GDPR, etc.)

---

**Built with ❤️ for better healthcare management**

*Last Updated: November 2025*
