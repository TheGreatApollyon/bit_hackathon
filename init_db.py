"""
Initialize database with test data
Creates admin user and sample organization
"""

import database as db
import auth

def init_test_data():
    """Initialize database with test users"""
    print("Initializing database...")
    db.init_db()
    
    # Create admin user
    admin_id = db.create_user(
        email='admin@healthcredx.com',
        password=auth.hash_password('admin123'),
        name='Admin User',
        role='admin'
    )
    
    if admin_id:
        print(f"✓ Created admin user: admin@healthcredx.com / admin123")
    
    # Create sample organization
    org_id = db.create_user(
        email='hospital@example.com',
        password=auth.hash_password('hospital123'),
        name='Medical Verifier',
        role='organization',
        organization_name='City Medical Center'
    )
    
    if org_id:
        print(f"✓ Created organization: hospital@example.com / hospital123")
    
    # Create sample practitioner
    prac_id = db.create_user(
        email='doctor@example.com',
        password=auth.hash_password('doctor123'),
        name='Dr. Jane Smith',
        role='practitioner',
        practitioner_type='Doctor'
    )
    
    if prac_id:
        print(f"✓ Created practitioner: doctor@example.com / doctor123")
    
    print("\n" + "=" * 60)
    print("Database initialized successfully!")
    print("=" * 60)

if __name__ == '__main__':
    init_test_data()
