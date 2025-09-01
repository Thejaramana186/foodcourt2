from flask import Blueprint, request, jsonify, current_app
from db import db
from models.cart import Cart
from flask_login import current_user, login_required

cart_bp = Blueprint("cart", __name__)

# ----------------------------
# Count items in cart
# ----------------------------
@cart_bp.route("/count")
@login_required
def cart_count():
    try:
        count = Cart.query.filter_by(user_id=current_user.id).count()
        return jsonify({"count": count})
    except Exception as e:
        current_app.logger.error(f"Cart Count Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ----------------------------
# Add item to cart
# ----------------------------
@cart_bp.route('/add', methods=['POST'])
@login_required
def add_to_cart():
    try:
        data = request.get_json()
        current_app.logger.debug(f"Cart Add Payload: {data}")

        menu_id = data.get('menu_id')
        quantity = data.get('quantity', 1)

        if not menu_id:
            return jsonify({"error": "menu_id is required"}), 400

        cart_item = Cart(user_id=current_user.id, menu_id=menu_id, quantity=quantity)
        db.session.add(cart_item)
        db.session.commit()

        return jsonify({"message": "Item added to cart successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Cart Add Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ----------------------------
# Update item quantity/customization
# ----------------------------
@cart_bp.route("/update", methods=["POST"])
@login_required
def update_cart():
    data = request.get_json()
    if not data or "cart_id" not in data:
        return jsonify({"error": "cart_id is required"}), 400

    cart_item = Cart.query.filter_by(id=data["cart_id"], user_id=current_user.id).first()
    if not cart_item:
        return jsonify({"error": "Cart item not found"}), 404

    try:
        cart_item.quantity = data.get("quantity", cart_item.quantity)
        cart_item.customization = data.get("customization", getattr(cart_item, "customization", None))
        db.session.commit()
        return jsonify({"message": "Cart updated"}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Cart Update Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ----------------------------
# Remove item from cart
# ----------------------------
@cart_bp.route("/remove", methods=["POST"])
@login_required
def remove_cart():
    data = request.get_json()
    if not data or "cart_id" not in data:
        return jsonify({"error": "cart_id is required"}), 400

    cart_item = Cart.query.filter_by(id=data["cart_id"], user_id=current_user.id).first()
    if not cart_item:
        return jsonify({"error": "Cart item not found"}), 404

    try:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({"message": "Cart item removed"}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Cart Remove Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ----------------------------
# Clear entire cart
# ----------------------------
@cart_bp.route("/clear", methods=["POST"])
@login_required
def clear_cart():
    try:
        Cart.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        return jsonify({"message": "Cart cleared"}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Cart Clear Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
