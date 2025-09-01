from flask import Blueprint, request, render_template, redirect, url_for, session, flash, jsonify
from utils.auth import login_required, delivery_person_required, get_current_user
from dao.order_dao import OrderDAO
from datetime import datetime

delivery_bp = Blueprint('delivery', __name__, url_prefix='/delivery')
order_dao = OrderDAO()

@delivery_bp.route('/dashboard')
@login_required
@delivery_person_required
def dashboard():
    user = get_current_user()
    
    # Get delivery statistics
    stats = order_dao.get_delivery_person_statistics(user.id)
    
    # Get assigned orders
    assigned_orders = order_dao.get_orders_by_delivery_person(user.id, status_filter='assigned')
    
    # ✅ FIX: Fetch available orders (missing earlier)
    available_orders = order_dao.get_available_orders_for_delivery()   # UPDATED
    
    # Get recent deliveries
    recent_deliveries = order_dao.get_orders_by_delivery_person(user.id, page=1, per_page=10)
    
    return render_template(
        'delivery/dashboard.html',
        user=user,
        stats=stats,
        assigned_orders=assigned_orders,       # no `.items` so template can paginate if needed
        available_orders=available_orders,     # UPDATED
        recent_deliveries=recent_deliveries
    )

@delivery_bp.route('/orders')
@login_required
@delivery_person_required
def orders():
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    orders = order_dao.get_orders_by_delivery_person(
        user.id, page=page, per_page=15, status_filter=status_filter
    )
    
    return render_template('delivery/orders.html', orders=orders, status_filter=status_filter)

@delivery_bp.route('/available_orders')
@login_required
@delivery_person_required
def available_orders():
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    
    # Get orders ready for pickup that don't have a delivery person assigned
    available_orders = order_dao.get_available_orders_for_delivery(page=page, per_page=15)
    
    return render_template('delivery/available_orders.html', orders=available_orders)

@delivery_bp.route('/order/<int:order_id>/accept', methods=['POST'])
@login_required
@delivery_person_required
def accept_order(order_id):
    user = get_current_user()
    order = order_dao.get_order_by_id(order_id)
    
    if not order:
        flash("Order not found", "danger")   # ✅ Show flash message
        return redirect(url_for('delivery.dashboard'))   # ✅ Redirect instead of JSON
    
    if order.status != 'ready_for_pickup' or order.delivery_person_id:
        flash("Order not available for pickup", "warning")   # ✅ Flash message
        return redirect(url_for('delivery.dashboard'))   # ✅ Redirect
    
    # Assign delivery person
    order.delivery_person_id = user.id
    order.status = 'out_for_delivery'
    order.pickup_at = datetime.utcnow()
    
    if order_dao.update_order(order):
        flash("Order accepted successfully", "success")   # ✅ Flash message
    else:
        flash("Failed to accept order", "danger")   # ✅ Flash message
    
    # ✅ Always redirect back to delivery dashboard
    return redirect(url_for('delivery.dashboard'))



@delivery_bp.route('/order/<int:order_id>/update_status', methods=['POST'])
@login_required
@delivery_person_required
def update_delivery_status(order_id):
    user = get_current_user()
    order = order_dao.get_order_by_id(order_id)
    
    if not order or order.delivery_person_id != user.id:
        return jsonify({'error': 'Order not found or access denied'}), 404
    
    new_status = request.json.get('status')
    
    if new_status == 'delivered':
        order.status = 'delivered'
        order.delivered_at = datetime.utcnow()
        order.actual_delivery_time = datetime.utcnow()
    else:
        return jsonify({'error': 'Invalid status'}), 400
    
    if order_dao.update_order(order):
        return jsonify({'message': 'Delivery status updated successfully'})
    else:
        return jsonify({'error': 'Failed to update status'}), 500

@delivery_bp.route('/earnings')
@login_required
@delivery_person_required
def earnings():
    user = get_current_user()
    
    # Get earnings data (this would need a proper earnings/commission system)
    earnings_data = order_dao.get_delivery_earnings(user.id)
    
    return render_template('delivery/earnings.html', earnings_data=earnings_data)
