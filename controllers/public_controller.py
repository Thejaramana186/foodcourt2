from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from dao.restaurant_dao import RestaurantDAO
from dao.menu_dao import MenuDAO

public_bp = Blueprint('public', __name__)
restaurant_dao = RestaurantDAO()
menu_dao = MenuDAO()

@public_bp.route('/')
def index():
    # Get featured restaurants
    featured_restaurants = restaurant_dao.get_featured_restaurants(limit=8)
    
    # Get popular cuisines
    cuisines = restaurant_dao.get_all_cuisines()[:8]
    
    # Get some statistics for the homepage
    stats = {
        'total_restaurants': restaurant_dao.get_restaurant_count(),
        'total_orders': 'Coming Soon',  # Would need proper implementation
        'happy_customers': 'Coming Soon'
    }
    
    return render_template('public/index.html', 
                         restaurants=featured_restaurants, 
                         cuisines=cuisines,
                         stats=stats)

@public_bp.route('/restaurants')
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
        sort_by=sort_by,
        verified_only=True
    )
    
    cuisines = restaurant_dao.get_all_cuisines()
    
    return render_template('public/restaurants.html',
                         restaurants=restaurants,
                         cuisines=cuisines,
                         search=search,
                         selected_cuisine=cuisine,
                         selected_type=type_filter,
                         sort_by=sort_by)

@public_bp.route('/restaurant/<int:restaurant_id>')
def restaurant_detail(restaurant_id):
    restaurant = restaurant_dao.get_restaurant_by_id(restaurant_id)
    
    if not restaurant or not restaurant.is_active or not restaurant.is_verified:
        return render_template('public/error.html', error="Restaurant not found"), 404
    
    # Get menu items
    category = request.args.get('category', '')
    type_filter = request.args.get('type', '')
    
    menus = menu_dao.get_menu_by_restaurant(restaurant_id, category, type_filter)
    categories = menu_dao.get_categories_by_restaurant(restaurant_id)
    
    return render_template('public/restaurant_detail.html',
                         restaurant=restaurant,
                         menus=menus,
                         categories=categories,
                         selected_category=category,
                         selected_type=type_filter)

@public_bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    
    if not query:
        return redirect(url_for('public.restaurants'))
    
    # Search restaurants
    restaurants = restaurant_dao.search_restaurants(query, page=page, per_page=12)
    
    # Search menu items
    menu_items = menu_dao.search_menu_items(query, page=1, per_page=20)
    
    return render_template('public/search_results.html',
                         query=query,
                         restaurants=restaurants,
                         menu_items=menu_items)

@public_bp.route('/about')
def about():
    return render_template('public/about.html')

@public_bp.route('/contact')
def contact():
    return render_template('public/contact.html')

@public_bp.route('/privacy')
def privacy():
    return render_template('public/privacy.html')

@public_bp.route('/terms')
def terms():
    return render_template('public/terms.html')