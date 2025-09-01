"""
Debug script to check database contents
Run this with: python debug_db.py
"""
from app import create_app
from models.restaurant import Restaurant
from models.menu import Menu
from models.user import User

def debug_database():
    app = create_app()
    
    with app.app_context():
        print("=== DATABASE DEBUG INFO ===")
        
        # Check users
        users = User.query.all()
        print(f"\nUsers in database: {len(users)}")
        for user in users:
            print(f"  - {user.username} ({user.role})")
        
        # Check restaurants
        restaurants = Restaurant.query.all()
        print(f"\nRestaurants in database: {len(restaurants)}")
        for restaurant in restaurants:
            print(f"  - ID: {restaurant.id}, Name: {restaurant.name}, Verified: {restaurant.is_verified}")
        
        # Check menu items
        menus = Menu.query.all()
        print(f"\nMenu items in database: {len(menus)}")
        for menu in menus:
            print(f"  - {menu.name} (Restaurant ID: {menu.restaurant_id})")
        
        print("\n=== END DEBUG INFO ===")

if __name__ == '__main__':
    debug_database()