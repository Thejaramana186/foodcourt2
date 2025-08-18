from flask import Blueprint, request, render_template, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from dao.user_dao import UserDAO
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__)
user_dao = UserDAO()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        
        # Validation
        if not username or not password:
            flash('Please fill in all fields', 'error')
            return render_template('auth/login.html')
        
        # Get user by username or email
        user = user_dao.get_user_by_username(username)
        if not user:
            user = user_dao.get_user_by_email(username)
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'error')
                return render_template('auth/login.html')
            
            # Update last login
            user.last_login = datetime.utcnow()
            user_dao.update_user(user)
            
            # Set session
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_role'] = user.role
            session['user_name'] = user.get_full_name()
            
            # Set session permanency
            if remember_me:
                session.permanent = True
            
            flash(f'Welcome back, {user.first_name}!', 'success')
            
            # Redirect based on role
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'restaurant_owner':
                return redirect(url_for('restaurant_owner.dashboard'))
            elif user.role == 'delivery_person':
                return redirect(url_for('delivery.dashboard'))
            else:
                return redirect(url_for('customer.dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        role = request.form.get('role', 'customer')
        
        # Validation
        errors = []
        
        if not all([username, email, password, confirm_password, first_name, last_name]):
            errors.append('Please fill in all required fields')
        
        if len(username) < 3:
            errors.append('Username must be at least 3 characters long')
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append('Username can only contain letters, numbers, and underscores')
        
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors.append('Please enter a valid email address')
        
        if len(password) < 6:
            errors.append('Password must be at least 6 characters long')
        
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        if phone and not re.match(r'^\d{10}$', phone):
            errors.append('Phone number must be exactly 10 digits')
        
        if role not in ['customer', 'restaurant_owner', 'delivery_person']:
            errors.append('Invalid user role selected')
        
        # Check for existing users
        if user_dao.get_user_by_username(username):
            errors.append('Username already exists')
        
        if user_dao.get_user_by_email(email):
            errors.append('Email already registered')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            address=address,
            city=city,
            role=role,
            is_verified=True  # Auto-verify for demo
        )
        user.set_password(password)
        
        if user_dao.create_user(user):
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    user_role = session.get('user_role', 'customer')
    username = session.get('username', '')
    
    session.clear()
    flash(f'You have been logged out successfully. Come back soon!', 'success')
    
    return redirect(url_for('public.index'))

@auth_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please log in to view your profile.', 'error')
        return redirect(url_for('auth.login'))
    
    user = user_dao.get_user_by_id(session['user_id'])
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/profile.html', user=user)

@auth_bp.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = user_dao.get_user_by_id(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Update user data
    user.first_name = request.form.get('first_name', user.first_name).strip()
    user.last_name = request.form.get('last_name', user.last_name).strip()
    user.phone = request.form.get('phone', user.phone)
    user.address = request.form.get('address', user.address)
    user.city = request.form.get('city', user.city)
    
    if user_dao.update_user(user):
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
    else:
        flash('Failed to update profile. Please try again.', 'error')
        return redirect(url_for('auth.profile'))

@auth_bp.route('/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = user_dao.get_user_by_id(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    # Validation
    if not user.check_password(current_password):
        flash('Current password is incorrect', 'error')
        return redirect(url_for('auth.profile'))
    
    if len(new_password) < 6:
        flash('New password must be at least 6 characters long', 'error')
        return redirect(url_for('auth.profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match', 'error')
        return redirect(url_for('auth.profile'))
    
    # Update password
    user.set_password(new_password)
    if user_dao.update_user(user):
        flash('Password changed successfully!', 'success')
    else:
        flash('Failed to change password. Please try again.', 'error')
    
    return redirect(url_for('auth.profile'))