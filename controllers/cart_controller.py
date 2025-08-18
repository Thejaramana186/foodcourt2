from flask import Blueprint, request, render_template, redirect, url_for, session, flash, jsonify
from utils.auth import login_required, customer_required, get_current_user
from models.cart import Cart
from models.menu import Menu
from dao.cart_dao import CartDAO

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')
cart_dao = CartDAO()

@cart_bp.route('/add', methods=['POST'])
@login_required
@customer_required
def add_to_cart():
    user = get_current_user()
    data = request.get_json()
    
    menu_id = data.get('menu_id')
    quantity = data.get('quantity', 1)
    customization = data.get('customization', '')
    
    if not menu_id:
        return jsonify({'error': 'Menu ID is required'}), 400
    
    if quantity <= 0:
        return jsonify({'error': 'Quantity must be greater than 0'}), 400
    
    # Check if menu item exists and is available
    menu_item = Menu.query.get(menu_id)
    if not menu_item or not menu_item.is_available:
        return jsonify({'error': 'Menu item not found or not available'}), 404
    
    # Check if restaurant is active and verified
    if not menu_item.restaurant.is_active or not menu_item.restaurant.is_verified:
        return jsonify({'error': 'Restaurant is currently unavailable'}), 400
    
    # Add to cart
    cart_item = cart_dao.add_to_cart(user.id, menu_id, quantity, customization)
    
    if cart_item:
        return jsonify({
            'message': 'Item added to cart successfully',
            'cart_item': cart_item.to_dict(),
            'cart_count': cart_dao.get_cart_count(user.id)
        })
    else:
        return jsonify({'error': 'Failed to add item to cart'}), 500

@cart_bp.route('/update', methods=['POST'])
@login_required
@customer_required
def update_cart():
    user = get_current_user()
    data = request.get_json()
    
    cart_id = data.get('cart_id')
    quantity = data.get('quantity')
    
    if not cart_id or quantity is None:
        return jsonify({'error': 'Cart ID and quantity are required'}), 400
    
    if quantity <= 0:
        # Remove item from cart
        if cart_dao.remove_from_cart(user.id, cart_id):
            return jsonify({
                'message': 'Item removed from cart',
                'cart_count': cart_dao.get_cart_count(user.id)
            })
        else:
            return jsonify({'error': 'Failed to remove item from cart'}), 500
    else:
        # Update quantity
        cart_item = cart_dao.update_cart_quantity(user.id, cart_id, quantity)
        if cart_item:
            return jsonify({
                'message': 'Cart updated successfully',
                'cart_item': cart_item.to_dict(),
                'cart_count': cart_dao.get_cart_count(user.id)
            })
        else:
            return jsonify({'error': 'Failed to update cart'}), 500

@cart_bp.route('/remove', methods=['POST'])
@login_required
@customer_required
def remove_from_cart():
    user = get_current_user()
    data = request.get_json()
    
    cart_id = data.get('cart_id')
    
    if not cart_id:
        return jsonify({'error': 'Cart ID is required'}), 400
    
    if cart_dao.remove_from_cart(user.id, cart_id):
        return jsonify({
            'message': 'Item removed from cart successfully',
            'cart_count': cart_dao.get_cart_count(user.id)
        })
    else:
        return jsonify({'error': 'Failed to remove item from cart'}), 500

@cart_bp.route('/clear', methods=['POST'])
@login_required
@customer_required
def clear_cart():
    user = get_current_user()
    
    if cart_dao.clear_cart(user.id):
        return jsonify({'message': 'Cart cleared successfully'})
    else:
        return jsonify({'error': 'Failed to clear cart'}), 500

@cart_bp.route('/count')
@login_required
@customer_required
def cart_count():
    user = get_current_user()
    count = cart_dao.get_cart_count(user.id)
    return jsonify({'count': count})