from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify
from models.user import User

def login_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('auth.login'))
            
            user = User.query.get(session['user_id'])
            if not user or user.role not in roles:
                if request.is_json:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('dashboard.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator to require admin role"""
    return role_required('admin')(f)

def restaurant_owner_required(f):
    """Decorator to require restaurant owner role"""
    return role_required('restaurant_owner')(f)

def delivery_person_required(f):
    """Decorator to require delivery person role"""
    return role_required('delivery_person')(f)

def customer_required(f):
    """Decorator to require customer role"""
    return role_required('customer')(f)

def get_current_user():
    """Get the current logged-in user"""
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])

def is_authenticated():
    """Check if user is authenticated"""
    return 'user_id' in session

def has_role(role):
    """Check if current user has specific role"""
    user = get_current_user()
    return user and user.role == role

def has_any_role(*roles):
    """Check if current user has any of the specified roles"""
    user = get_current_user()
    return user and user.role in roles