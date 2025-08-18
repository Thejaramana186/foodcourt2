from flask import Blueprint, request, render_template, redirect, url_for, session, flash, jsonify
from utils.auth import login_required, restaurant_owner_required, get_current_user
from dao.restaurant_dao import RestaurantDAO
from dao.menu_dao import MenuDAO
from dao.order_dao import OrderDAO
from models.restaurant import Restaurant
from models.menu import Menu
from datetime import datetime, timedelta

restaurant_owner_bp = Blueprint('restaurant_owner', __name__, url_prefix='/restaurant-owner')
restaurant_dao = RestaurantDAO()
menu_dao = MenuDAO()
order_dao = OrderDAO()

@restaurant_owner_bp.route('/dashboard')
@login_required
@restaurant_owner_required
def dashboard():
    user = get_current_user()
    
    # Get owner's restaurants - handle pagination object properly
    restaurants_pagination = restaurant_dao.get_restaurants_by_owner(user.id)
    
    # Check if it's a pagination object or a list
    if hasattr(restaurants_pagination, 'items'):
        restaurants = restaurants_pagination.items
        total_restaurants = restaurants_pagination.total
    else:
        restaurants = restaurants_pagination
        total_restaurants = len(restaurants)
    
    # Get statistics
    total_orders = 0
    total_revenue = 0
    pending_orders = 0
    
    for restaurant in restaurants:
        restaurant_stats = order_dao.get_restaurant_statistics(restaurant.id)
        total_orders += restaurant_stats['total_orders']
        total_revenue += restaurant_stats['total_revenue']
        pending_orders += restaurant_stats['pending_orders']
    
    # Get recent orders from first 3 restaurants
    recent_orders = []
    for restaurant in restaurants[:3]:
        restaurant_orders = order_dao.get_orders_by_restaurant(restaurant.id, page=1, per_page=5)
        if hasattr(restaurant_orders, 'items'):
            recent_orders.extend(restaurant_orders.items)
        else:
            recent_orders.extend(restaurant_orders)
    
    # Sort by created_at and limit to 10
    recent_orders = sorted(recent_orders, key=lambda x: x.created_at, reverse=True)[:10]
    
    stats = {
        'total_restaurants': total_restaurants,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders
    }
    
    return render_template('restaurant_owner/dashboard.html',
                         user=user,
                         restaurants=restaurants,
                         stats=stats,
                         recent_orders=recent_orders)

@restaurant_owner_bp.route('/restaurants')
@login_required
@restaurant_owner_required
def restaurants():
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    
    restaurants = restaurant_dao.get_restaurants_by_owner(user.id, page=page, per_page=10)
    
    return render_template('restaurant_owner/restaurants.html', restaurants=restaurants)

@restaurant_owner_bp.route('/restaurant/add', methods=['GET', 'POST'])
@login_required
@restaurant_owner_required
def add_restaurant():
    user = get_current_user()
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        cuisine = request.form.get('cuisine', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        type_food = request.form.get('type', 'both')
        opening_time = request.form.get('opening_time', '')
        closing_time = request.form.get('closing_time', '')
        delivery_fee = request.form.get('delivery_fee', 0, type=float)
        minimum_order = request.form.get('minimum_order', 0, type=float)
        
        # Validation
        if not all([name, cuisine, address, city, phone]):
            flash('Please fill in all required fields', 'error')
            return render_template('restaurant_owner/add_restaurant.html')
        
        # Create restaurant
        restaurant = Restaurant(
            name=name,
            description=description,
            cuisine=cuisine,
            address=address,
            city=city,
            phone=phone,
            email=email,
            type=type_food,
            opening_time=opening_time,
            closing_time=closing_time,
            delivery_fee=delivery_fee,
            minimum_order=minimum_order,
            owner_id=user.id,
            image='https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?auto=compress&cs=tinysrgb&w=400'
        )
        
        if restaurant_dao.create_restaurant(restaurant):
            flash('Restaurant added successfully!', 'success')
            return redirect(url_for('restaurant_owner.restaurants'))
        else:
            flash('Failed to add restaurant. Please try again.', 'error')
    
    return render_template('restaurant_owner/add_restaurant.html')

@restaurant_owner_bp.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
@login_required
@restaurant_owner_required
def edit_restaurant(restaurant_id):
    user = get_current_user()
    restaurant = restaurant_dao.get_restaurant_by_id(restaurant_id)
    
    if not restaurant or restaurant.owner_id != user.id:
        flash('Restaurant not found or access denied', 'error')
        return redirect(url_for('restaurant_owner.restaurants'))
    
    if request.method == 'POST':
        # Update restaurant data
        restaurant.name = request.form.get('name', restaurant.name).strip()
        restaurant.description = request.form.get('description', restaurant.description)
        restaurant.cuisine = request.form.get('cuisine', restaurant.cuisine)
        restaurant.address = request.form.get('address', restaurant.address)
        restaurant.city = request.form.get('city', restaurant.city)
        restaurant.phone = request.form.get('phone', restaurant.phone)
        restaurant.email = request.form.get('email', restaurant.email)
        restaurant.type = request.form.get('type', restaurant.type)
        restaurant.opening_time = request.form.get('opening_time', restaurant.opening_time)
        restaurant.closing_time = request.form.get('closing_time', restaurant.closing_time)
        restaurant.delivery_fee = request.form.get('delivery_fee', restaurant.delivery_fee, type=float)
        restaurant.minimum_order = request.form.get('minimum_order', restaurant.minimum_order, type=float)
        
        if restaurant_dao.update_restaurant(restaurant):
            flash('Restaurant updated successfully!', 'success')
            return redirect(url_for('restaurant_owner.restaurants'))
        else:
            flash('Failed to update restaurant', 'error')
    
    return render_template('restaurant_owner/edit_restaurant.html', restaurant=restaurant)

@restaurant_owner_bp.route('/restaurant/<int:restaurant_id>/menu')
@login_required
@restaurant_owner_required
def menu_management(restaurant_id):
    user = get_current_user()
    restaurant = restaurant_dao.get_restaurant_by_id(restaurant_id)
    
    if not restaurant or restaurant.owner_id != user.id:
        flash('Restaurant not found or access denied', 'error')
        return redirect(url_for('restaurant_owner.restaurants'))
    
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    
    menus = menu_dao.get_menu_by_restaurant(restaurant_id, category=category, page=page)
    categories = menu_dao.get_categories_by_restaurant(restaurant_id)
    
    return render_template('restaurant_owner/menu_management.html',
                         restaurant=restaurant,
                         menus=menus,
                         categories=categories,
                         selected_category=category)

@restaurant_owner_bp.route('/restaurant/<int:restaurant_id>/menu/add', methods=['GET', 'POST'])
@login_required
@restaurant_owner_required
def add_menu_item(restaurant_id):
    user = get_current_user()
    restaurant = restaurant_dao.get_restaurant_by_id(restaurant_id)
    
    if not restaurant or restaurant.owner_id != user.id:
        flash('Restaurant not found or access denied', 'error')
        return redirect(url_for('restaurant_owner.restaurants'))
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', 0, type=float)
        discounted_price = request.form.get('discounted_price', type=float)
        category = request.form.get('category', '').strip()
        type_food = request.form.get('type', 'veg')
        ingredients = request.form.get('ingredients', '').strip()
        allergens = request.form.get('allergens', '').strip()
        spice_level = request.form.get('spice_level', '')
        preparation_time = request.form.get('preparation_time', type=int)
        calories = request.form.get('calories', type=int)
        is_featured = request.form.get('is_featured') == 'on'
        
        # Validation
        if not all([name, price, category]) or price <= 0:
            flash('Please fill in all required fields with valid values', 'error')
            return render_template('restaurant_owner/add_menu_item.html', restaurant=restaurant)
        
        if discounted_price and discounted_price >= price:
            flash('Discounted price must be less than regular price', 'error')
            return render_template('restaurant_owner/add_menu_item.html', restaurant=restaurant)
        
        # Create menu item
        menu = Menu(
            restaurant_id=restaurant_id,
            name=name,
            description=description,
            price=price,
            discounted_price=discounted_price,
            category=category,
            type=type_food,
            ingredients=ingredients,
            allergens=allergens,
            spice_level=spice_level,
            preparation_time=preparation_time,
            calories=calories,
            is_featured=is_featured,
            image='https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?auto=compress&cs=tinysrgb&w=300'
        )
        
        if menu_dao.create_menu(menu):
            flash('Menu item added successfully!', 'success')
            return redirect(url_for('restaurant_owner.menu_management', restaurant_id=restaurant_id))
        else:
            flash('Failed to add menu item', 'error')
    
    return render_template('restaurant_owner/add_menu_item.html', restaurant=restaurant)

@restaurant_owner_bp.route('/orders')
@login_required
@restaurant_owner_required
def orders():
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    restaurant_id = request.args.get('restaurant_id', type=int)
    
    # Get user's restaurants - handle pagination properly
    user_restaurants_result = restaurant_dao.get_restaurants_by_owner(user.id)
    if hasattr(user_restaurants_result, 'items'):
        user_restaurants = user_restaurants_result.items
    else:
        user_restaurants = user_restaurants_result
    
    restaurant_ids = [r.id for r in user_restaurants]
    
    if restaurant_id and restaurant_id not in restaurant_ids:
        flash('Access denied', 'error')
        return redirect(url_for('restaurant_owner.orders'))
    
    orders = order_dao.get_orders_by_restaurants(
        restaurant_ids if not restaurant_id else [restaurant_id],
        page=page,
        per_page=15,
        status_filter=status_filter
    )
    
    return render_template('restaurant_owner/orders.html',
                         orders=orders,
                         restaurants=user_restaurants,
                         selected_restaurant=restaurant_id,
                         status_filter=status_filter)

@restaurant_owner_bp.route('/order/<int:order_id>/update_status', methods=['POST'])
@login_required
@restaurant_owner_required
def update_order_status(order_id):
    user = get_current_user()
    order = order_dao.get_order_by_id(order_id)
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    # Check if user owns the restaurant
    restaurant = restaurant_dao.get_restaurant_by_id(order.restaurant_id)
    if not restaurant or restaurant.owner_id != user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    new_status = request.json.get('status')
    valid_statuses = ['confirmed', 'preparing', 'ready_for_pickup']
    
    if new_status not in valid_statuses:
        return jsonify({'error': 'Invalid status'}), 400
    
    # Update status with timestamp
    order.status = new_status
    if new_status == 'confirmed':
        order.confirmed_at = datetime.utcnow()
    elif new_status == 'preparing':
        order.prepared_at = datetime.utcnow()
    elif new_status == 'ready_for_pickup':
        order.pickup_at = datetime.utcnow()
    
    if order_dao.update_order(order):
        return jsonify({'message': 'Order status updated successfully'})
    else:
        return jsonify({'error': 'Failed to update order status'}), 500