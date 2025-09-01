from flask import Flask, render_template, g
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from db import db

# Import models
from models.user import User
from models.restaurant import Restaurant
from models.menu import Menu
from models.cart import Cart
from models.order import Order, OrderItem

# Auth utility
from utils.auth import get_current_user

# Import blueprints
from controllers.auth_controller import auth_bp
from controllers.customer_controller import customer_bp
from controllers.restaurant_owner_controller import restaurant_owner_bp
from controllers.delivery_controller import delivery_bp
from controllers.admin_controller import admin_bp
from controllers.public_controller import public_bp
from controllers.cart_controller import cart_bp
from controllers.checkout_controller import checkout_bp
from controllers.dashboard_controller import dashboard_bp

from datetime import datetime


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database + migration
    db.init_app(app)
    migrate = Migrate(app, db)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(customer_bp)
    app.register_blueprint(restaurant_owner_bp)
    app.register_blueprint(delivery_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(cart_bp, url_prefix="/cart")
    app.register_blueprint(checkout_bp)
    app.register_blueprint(dashboard_bp)

    # Global user load
    @app.before_request
    def load_current_user():
        g.current_user = get_current_user()

    @app.context_processor
    def inject_user():
        return dict(current_user=g.current_user)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    return app


def seed_data():
    """Seed initial data for demonstration"""

    if User.query.count() > 0:
        return

    # Create users
    admin = User(
        username="admin",
        email="admin@foodiehub.com",
        first_name="System",
        last_name="Administrator",
        role="admin",
        is_verified=True,
    )
    admin.set_password("admin123")
    db.session.add(admin)

    owner = User(
        username="restaurant_owner",
        email="owner@example.com",
        first_name="Restaurant",
        last_name="Owner",
        phone="9876543210",
        role="restaurant_owner",
        is_verified=True,
    )
    owner.set_password("owner123")
    db.session.add(owner)

    delivery = User(
        username="delivery_person",
        email="delivery@example.com",
        first_name="Delivery",
        last_name="Person",
        phone="9876543211",
        role="delivery_person",
        is_verified=True,
    )
    delivery.set_password("delivery123")
    db.session.add(delivery)

    customer = User(
        username="customer",
        email="customer@example.com",
        first_name="John",
        last_name="Doe",
        phone="9876543212",
        address="123 Main Street, City",
        role="customer",
        is_verified=True,
    )
    customer.set_password("customer123")
    db.session.add(customer)

    db.session.commit()

    # Restaurants
    restaurants_data = [
        {
            "name": "Spice Palace",
            "description": "Authentic North Indian cuisine with traditional flavors",
            "cuisine": "North Indian",
            "rating": 4.8,
            "delivery_time": "30-45 min",
            "type": "both",
            "address": "123 Food Street, Mumbai",
            "city": "mumbai",
            "phone": "022-12345678",
            "email": "spicepalace@example.com",
            "opening_time": "09:00",
            "closing_time": "23:00",
        },
        {
            "name": "Pizza Corner",
            "description": "Fresh Italian pizzas made with authentic ingredients",
            "cuisine": "Italian",
            "rating": 4.6,
            "delivery_time": "25-35 min",
            "type": "both",
            "address": "456 Pizza Lane, Delhi",
            "city": "delhi",
            "phone": "011-87654321",
            "email": "pizzacorner@example.com",
            "opening_time": "10:00",
            "closing_time": "24:00",
        },
        {
            "name": "Healthy Bites",
            "description": "Fresh salads, smoothies and healthy continental food",
            "cuisine": "Continental",
            "rating": 4.4,
            "delivery_time": "20-30 min",
            "type": "veg",
            "address": "789 Health Avenue, Bangalore",
            "city": "bangalore",
            "phone": "080-11223344",
            "email": "healthybites@example.com",
            "opening_time": "08:00",
            "closing_time": "22:00",
        },
    ]

    restaurant_images = [
        "https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?auto=compress&cs=tinysrgb&w=400",
        "https://images.pexels.com/photos/1639557/pexels-photo-1639557.jpeg?auto=compress&cs=tinysrgb&w=400",
        "https://images.pexels.com/photos/1410235/pexels-photo-1410235.jpeg?auto=compress&cs=tinysrgb&w=400",
    ]

    for i, r in enumerate(restaurants_data):
        restaurant = Restaurant(
            owner_id=owner.id,
            name=r["name"],
            description=r["description"],
            cuisine=r["cuisine"],
            rating=r["rating"],
            delivery_time=r["delivery_time"],
            type=r["type"],
            address=r["address"],
            city=r["city"],
            phone=r["phone"],
            email=r["email"],
            opening_time=r["opening_time"],
            closing_time=r["closing_time"],
            image=restaurant_images[i],
            is_verified=True,
        )
        db.session.add(restaurant)

    db.session.commit()

    # Menu items
    sample_menus = [
        {"restaurant_name": "Spice Palace", "name": "Butter Chicken", "price": 320, "description": "Rich and creamy tomato-based chicken curry", "category": "Main Course", "type": "non-veg"},
        {"restaurant_name": "Spice Palace", "name": "Paneer Butter Masala", "price": 280, "description": "Soft cottage cheese in creamy tomato gravy", "category": "Main Course", "type": "veg"},
        {"restaurant_name": "Spice Palace", "name": "Garlic Naan", "price": 60, "description": "Fresh baked bread with garlic and herbs", "category": "Bread", "type": "veg"},
        {"restaurant_name": "Pizza Corner", "name": "Margherita Pizza", "price": 240, "description": "Fresh mozzarella, tomato sauce, basil", "category": "Pizza", "type": "veg"},
        {"restaurant_name": "Pizza Corner", "name": "Pepperoni Pizza", "price": 320, "description": "Classic pepperoni with mozzarella cheese", "category": "Pizza", "type": "non-veg"},
        {"restaurant_name": "Pizza Corner", "name": "Caesar Salad", "price": 180, "description": "Crisp romaine lettuce with caesar dressing", "category": "Salad", "type": "veg"},
        {"restaurant_name": "Healthy Bites", "name": "Quinoa Bowl", "price": 220, "description": "Nutritious quinoa with fresh vegetables", "category": "Bowl", "type": "veg"},
        {"restaurant_name": "Healthy Bites", "name": "Green Smoothie", "price": 120, "description": "Spinach, apple, and banana smoothie", "category": "Beverage", "type": "veg"},
        {"restaurant_name": "Healthy Bites", "name": "Avocado Toast", "price": 160, "description": "Multigrain bread with fresh avocado", "category": "Breakfast", "type": "veg"},
    ]

    for menu in sample_menus:
        restaurant = Restaurant.query.filter_by(name=menu["restaurant_name"]).first()
        if restaurant:
            m = Menu(
                restaurant_id=restaurant.id,
                name=menu["name"],
                price=menu["price"],
                description=menu["description"],
                category=menu["category"],
                type=menu["type"],
                image="https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?auto=compress&cs=tinysrgb&w=300",
            )
            db.session.add(m)

    db.session.commit()

    print("Database seeded successfully!")
    print("Login credentials:")
    print("Admin: admin / admin123")
    print("Restaurant Owner: restaurant_owner / owner123")
    print("Delivery Person: delivery_person / delivery123")
    print("Customer: customer / customer123")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_data()
    app.run(debug=True, host="0.0.0.0", port=5000)
