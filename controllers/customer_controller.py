from flask import Blueprint, request, render_template, redirect, url_for, session, flash, jsonify
from utils.auth import login_required, customer_required, get_current_user
from dao.restaurant_dao import RestaurantDAO
from dao.cart_dao import CartDAO
from dao.order_dao import OrderDAO

customer_bp = Blueprint('customer', __name__, url_prefix='/customer')
restaurant_dao = RestaurantDAO()
cart_dao = CartDAO()
order_dao = OrderDAO()

@customer_bp.route('/dashboard')
@login_required
@customer_required
def dashboard():
    user = get_current_user()
    
    # Get recent orders
    recent_orders = order_dao.get_orders_by_user(user.id, page=1, per_page=5)
    
    # Get favorite restaurants (most ordered from)
    favorite_restaurants = restaurant_dao.get_featured_restaurants(limit=6)
    
    # Get cart count
    cart_count = cart_dao.get_cart_count(user.id)
    
    # Get user statistics
    user_stats = order_dao.get_user_statistics(user.id)
    
    return render_template('customer/dashboard.html', 
                         user=user,
                         recent_orders=recent_orders,
                         favorite_restaurants=favorite_restaurants,
                         cart_count=cart_count,
                         user_stats=user_stats)

@customer_bp.route('/restaurants')
@login_required
@customer_required
def restaurants():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    cuisine = request.args.get('cuisine', '')
    type_filter = request.args.get('type', '')
    sort_by = request.args.get('sort', 'rating')
    
    restaurants = restaurant_dao.get_restaurants(
        page=page,
        per_page=12,
        search=search,
        cuisine=cuisine,
        type_filter=type_filter,
        sort_by=sort_by
    )
    
    cuisines = restaurant_dao.get_all_cuisines()
    
    return render_template('customer/restaurants.html',
                         restaurants=restaurants,
                         cuisines=cuisines,
                         search=search,
                         selected_cuisine=cuisine,
                         selected_type=type_filter,
                         sort_by=sort_by)

@customer_bp.route('/cart')
@login_required
@customer_required
def cart():
    user = get_current_user()
    cart_items = cart_dao.get_cart_items(user.id)
    
    if not cart_items:
        return render_template('customer/cart.html', cart_items=[], total=0, restaurants={})
    
    # Group items by restaurant
    restaurants = {}
    total = 0
    
    for item in cart_items:
        restaurant_id = item.menu.restaurant_id
        if restaurant_id not in restaurants:
            restaurants[restaurant_id] = {
                'restaurant': item.menu.restaurant,
                'items': [],
                'subtotal': 0
            }
        restaurants[restaurant_id]['items'].append(item)
        restaurants[restaurant_id]['subtotal'] += item.get_total_price()
        total += item.get_total_price()
    
    return render_template('customer/cart.html', 
                         cart_items=cart_items,
                         restaurants=restaurants,
                         total=total)

@customer_bp.route('/orders')
@login_required
@customer_required
def orders():
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    orders = order_dao.get_orders_by_user(user.id, page=page, per_page=10, status_filter=status_filter)
    
    return render_template('customer/orders.html', orders=orders, status_filter=status_filter)

@customer_bp.route('/order/<int:order_id>')
@login_required
@customer_required
def order_detail(order_id):
    user = get_current_user()
    order = order_dao.get_order_by_id(order_id)
    
    if not order or order.user_id != user.id:
        flash('Order not found', 'error')
        return redirect(url_for('customer.orders'))
    
    return render_template('customer/order_detail.html', order=order)

@customer_bp.route('/favorites')
@login_required
@customer_required
def favorites():
    user = get_current_user()
    # Implementation for favorites (would need a favorites table)
    return render_template('customer/favorites.html')

@customer_bp.route('/api/cart_count')
@login_required
@customer_required
def api_cart_count():
    user = get_current_user()
    count = cart_dao.get_cart_count(user.id)
    return jsonify({'count': count})