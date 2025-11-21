"""
Authentication and authorization utilities for HealthCredX
Session-based authentication with role-based access control
"""

from functools import wraps
from flask import session, redirect, url_for, flash
import database as db

def login_user(user):
    """Set session for logged-in user"""
    session['user_id'] = user['id']
    session['user_email'] = user['email']
    session['user_name'] = user['name']
    session['user_role'] = user['role']
    session['practitioner_type'] = user.get('practitioner_type')
    session['organization_name'] = user.get('organization_name')
    db.update_last_login(user['id'])

def logout_user():
    """Clear session"""
    session.clear()

def get_current_user():
    """Get current logged-in user"""
    if 'user_id' in session:
        return {
            'id': session['user_id'],
            'email': session['user_email'],
            'name': session['user_name'],
            'role': session['user_role'],
            'practitioner_type': session.get('practitioner_type'),
            'organization_name': session.get('organization_name')
        }
    return None

def is_authenticated():
    """Check if user is logged in"""
    return 'user_id' in session

def require_login(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def require_role(*roles):
    """Decorator to require specific role(s)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not is_authenticated():
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
            
            user = get_current_user()
            if user['role'] not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def check_permission(user_role, required_roles):
    """Check if user role has permission"""
    return user_role in required_roles

# Simple password hashing (for demo purposes - use bcrypt in production)
def hash_password(password):
    """Hash password (simplified for demo)"""
    # In production, use: bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return password  # For demo, storing plain text

def verify_password(password, hashed):
    """Verify password (simplified for demo)"""
    # In production, use: bcrypt.checkpw(password.encode('utf-8'), hashed)
    return password == hashed
