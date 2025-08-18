from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from utils.auth import login_required, customer_required, get_current_user
from models.order import Order, OrderItem
from dao.cart_dao import CartDAO
from dao.order_dao import OrderDAO
from datetime import datetime, timedelta
from db import db

checkout_bp = Blueprint('checkout', __name__, url_prefix='/checkout')
cart_dao = CartDAO()
order_dao = OrderDAO()

@checkout_bp.route('/')
@login_required
@customer_required
def checkout():
    user = get_current_user()
    cart_items = cart_dao.get_cart_items(user.id)
    
    if not cart_items:
        flash('Your cart is empty', 'error')
        return redirect(url_for('customer.cart'))
    
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
    
    # Calculate totals
    delivery_fee = 0  # Free delivery for demo
    tax_amount = total * 0.05  # 5% tax
    grand_total = total + delivery_fee + tax_amount
    
    return render_template('customer/checkout.html',
                         cart_items=cart_items,
                         restaurants=restaurants,
                         subtotal=total,
                         delivery_fee=delivery_fee,
                         tax_amount=tax_amount,
                         grand_total=grand_total,
                         user=user)

@checkout_bp.route('/place_order', methods=['POST'])
@login_required
@customer_required
def place_order():
    user = get_current_user()
    
    # Get form data
    booking_name = request.form.get('booking_name', '').strip()
    booking_email = request.form.get('booking_email', '').strip()
    phone = request.form.get('phone', '').strip()
    delivery_address = request.form.get('delivery_address', '').strip()
    delivery_city = request.form.get('delivery_city', '').strip()
    delivery_pincode = request.form.get('delivery_pincode', '').strip()
    delivery_date_str = request.form.get('delivery_date', '')
    delivery_time = request.form.get('delivery_time', '')
    payment_method = request.form.get('payment_method', '')
    special_instructions = request.form.get('special_instructions', '')
    
    # Validation
    if not all([booking_name, phone, delivery_address, payment_method]):
        flash('Please fill in all required fields', 'error')
        return redirect(url_for('checkout.checkout'))
    
    # Parse delivery date
    delivery_date = None
    if delivery_date_str:
        try:
            delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date()
        except ValueError:
            delivery_date = datetime.now().date()
    
    # Get cart items
    cart_items = cart_dao.get_cart_items(user.id)
    
    if not cart_items:
        flash('Your cart is empty', 'error')
        return redirect(url_for('customer.cart'))
    
    # Group items by restaurant
    restaurants_orders = {}
    for item in cart_items:
        restaurant_id = item.menu.restaurant_id
        if restaurant_id not in restaurants_orders:
            restaurants_orders[restaurant_id] = []
        restaurants_orders[restaurant_id].append(item)
    
    order_ids = []
    
    # Create separate orders for each restaurant
    for restaurant_id, items in restaurants_orders.items():
        subtotal = sum(item.get_total_price() for item in items)
        delivery_fee = 0  # Free delivery
        tax_amount = subtotal * 0.05  # 5% tax
        total_amount = subtotal + delivery_fee + tax_amount
        
        # Calculate estimated delivery time
        estimated_delivery = datetime.now() + timedelta(minutes=45)
        
        # Create order
        order = Order(
            user_id=user.id,
            restaurant_id=restaurant_id,
            total_amount=total_amount,
            delivery_fee=delivery_fee,
            tax_amount=tax_amount,
            booking_name=booking_name,
            booking_email=booking_email,
            phone=phone,
            delivery_address=delivery_address,
            delivery_city=delivery_city,
            delivery_pincode=delivery_pincode,
            delivery_date=delivery_date,
            delivery_time=delivery_time,
            payment_method=payment_method,
            special_instructions=special_instructions,
            estimated_delivery_time=estimated_delivery
        )
        
        try:
            db.session.add(order)
            db.session.flush()  # Get order ID
            order_id = order.id
            
            # Create order items
            for item in items:
                order_item = OrderItem(
                    order_id=order_id,
                    menu_id=item.menu_id,
                    quantity=item.quantity,
                    price=item.menu.get_effective_price(),
                    customization=item.customization
                )
                db.session.add(order_item)
            
            order_ids.append(order_id)
            
        except Exception as e:
            print(f"Error creating order: {e}")
            db.session.rollback()
            flash('Failed to place order. Please try again.', 'error')
            return redirect(url_for('checkout.checkout'))
    
    # Commit all orders
    try:
        db.session.commit()
        cart_dao.clear_cart(user.id)
        
        flash(f'Order placed successfully! Order numbers: {", ".join([f"ORD{oid}" for oid in order_ids])}', 'success')
        return redirect(url_for('customer.orders'))
        
    except Exception as e:
        print(f"Error committing orders: {e}")
        db.session.rollback()
        flash('Failed to place order. Please try again.', 'error')
        return redirect(url_for('checkout.checkout'))