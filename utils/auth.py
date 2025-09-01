from flask import session, g, redirect, url_for, flash
from flask_login import login_user as flask_login_user, logout_user as flask_logout_user, current_user
from functools import wraps
from models.user import User

def get_current_user():
    """Get current user from session"""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

def login_user_session(user):
    """Login user in both custom session and Flask-Login"""
    session['user_id'] = user.id
    session['user_role'] = user.role
    flask_login_user(user)

def logout_user_session():
    """Logout user from both custom session and Flask-Login"""
    session.pop('user_id', None)
    session.pop('user_role', None)
    flask_logout_user()

def login_required(f):
    """Decorator to require user to be logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.current_user:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def customer_required(f):
    """Decorator to require customer role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.current_user:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        if not g.current_user.is_customer():
            flash('Access denied. Customer access required.', 'error')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated_function

def restaurant_owner_required(f):
    """Decorator to require restaurant owner role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.current_user:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        if not g.current_user.is_restaurant_owner():
            flash('Access denied. Restaurant owner access required.', 'error')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated_function

def delivery_required(f):
    """Decorator to require delivery person role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.current_user:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        if not g.current_user.is_delivery_person():
            flash('Access denied. Delivery person access required.', 'error')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.current_user:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        if not g.current_user.is_admin():
            flash('Access denied. Admin access required.', 'error')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated_function

def delivery_person_required(f):
    """Decorator to require delivery person role (alias for delivery_required)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.current_user:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        if not g.current_user.is_delivery_person():
            flash('Access denied. Delivery person access required.', 'error')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated_function

def require_role(role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user or g.current_user.role != role:
                flash('Access denied.', 'error')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator