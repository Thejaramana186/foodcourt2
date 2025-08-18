from flask import Blueprint, request, render_template, redirect, url_for, session, flash, jsonify
from utils.auth import login_required, admin_required, get_current_user
from dao.user_dao import UserDAO
from dao.restaurant_dao import RestaurantDAO
from dao.order_dao import OrderDAO
from models.user import User
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
user_dao = UserDAO()
restaurant_dao = RestaurantDAO()
order_dao = OrderDAO()

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    user = get_current_user()
    
    # Get system statistics
    total_users = user_dao.get_user_count()
    total_restaurants = restaurant_dao.get_restaurant_count()
    total_orders = order_dao.get_total_order_count()
    total_revenue = order_dao.get_total_revenue()
    
    # Get recent activities
    recent_users = user_dao.get_recent_users(limit=5)
    recent_restaurants = restaurant_dao.get_recent_restaurants(limit=5)
    recent_orders = order_dao.get_recent_orders(limit=10)
    
    # Get daily statistics for the last 7 days
    daily_stats = []
    for i in range(7):
        date = datetime.now().date() - timedelta(days=i)
        day_stats = order_dao.get_daily_statistics(date)
        daily_stats.append({
            'date': date.strftime('%Y-%m-%d'),
            'orders': day_stats['orders'],
            'revenue': day_stats['revenue']
        })
    
    stats = {
        'total_users': total_users,
        'total_restaurants': total_restaurants,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'customers': user_dao.get_user_count_by_role('customer'),
        'restaurant_owners': user_dao.get_user_count_by_role('restaurant_owner'),
        'delivery_persons': user_dao.get_user_count_by_role('delivery_person')
    }
    
    return render_template('admin/dashboard.html',
                         user=user,
                         stats=stats,
                         recent_users=recent_users,
                         recent_restaurants=recent_restaurants,
                         recent_orders=recent_orders,
                         daily_stats=daily_stats)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    role_filter = request.args.get('role', '')
    search = request.args.get('search', '')
    
    users = user_dao.get_all_users(page=page, per_page=20, role_filter=role_filter, search=search)
    
    return render_template('admin/users.html', 
                         users=users, 
                         role_filter=role_filter, 
                         search=search)

@admin_bp.route('/user/<int:user_id>/toggle_status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    user = user_dao.get_user_by_id(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.role == 'admin':
        return jsonify({'error': 'Cannot modify admin users'}), 400
    
    user.is_active = not user.is_active
    
    if user_dao.update_user(user):
        status = 'activated' if user.is_active else 'deactivated'
        return jsonify({'message': f'User {status} successfully'})
    else:
        return jsonify({'error': 'Failed to update user status'}), 500

@admin_bp.route('/restaurants')
@login_required
@admin_required
def restaurants():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    
    restaurants = restaurant_dao.get_all_restaurants_admin(
        page=page, 
        per_page=20, 
        search=search, 
        status_filter=status_filter
    )
    
    return render_template('admin/restaurants.html',
                         restaurants=restaurants,
                         search=search,
                         status_filter=status_filter)

@admin_bp.route('/restaurant/<int:restaurant_id>/toggle_verification', methods=['POST'])
@login_required
@admin_required
def toggle_restaurant_verification(restaurant_id):
    restaurant = restaurant_dao.get_restaurant_by_id(restaurant_id)
    
    if not restaurant:
        return jsonify({'error': 'Restaurant not found'}), 404
    
    restaurant.is_verified = not restaurant.is_verified
    
    if restaurant_dao.update_restaurant(restaurant):
        status = 'verified' if restaurant.is_verified else 'unverified'
        return jsonify({'message': f'Restaurant {status} successfully'})
    else:
        return jsonify({'error': 'Failed to update restaurant verification'}), 500

@admin_bp.route('/orders')
@login_required
@admin_required
def orders():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    orders = order_dao.get_all_orders(page=page, per_page=20, status_filter=status_filter)
    
    return render_template('admin/orders.html', orders=orders, status_filter=status_filter)

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    # Get comprehensive analytics data
    analytics_data = {
        'user_growth': user_dao.get_user_growth_data(),
        'order_trends': order_dao.get_order_trends(),
        'revenue_analytics': order_dao.get_revenue_analytics(),
        'popular_cuisines': restaurant_dao.get_cuisine_popularity(),
        'top_restaurants': restaurant_dao.get_top_restaurants_by_revenue(),
        'delivery_performance': order_dao.get_delivery_performance_metrics()
    }
    
    return render_template('admin/analytics.html', analytics_data=analytics_data)