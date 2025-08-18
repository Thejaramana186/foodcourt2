from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from utils.auth import login_required, get_current_user

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    user = get_current_user()
    
    # Redirect to appropriate dashboard based on role
    if user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif user.role == 'restaurant_owner':
        return redirect(url_for('restaurant_owner.dashboard'))
    elif user.role == 'delivery_person':
        return redirect(url_for('delivery.dashboard'))
    else:  # customer
        return redirect(url_for('customer.dashboard'))