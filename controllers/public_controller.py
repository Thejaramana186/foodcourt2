from flask import Blueprint, render_template, request
from models.restaurant import Restaurant
from models.menu import Menu
from db import db

# Blueprint for all public-facing routes
public_bp = Blueprint('public', __name__, url_prefix='/')


@public_bp.route('/')
def index():
    """Home page showing featured restaurants"""
    restaurants = (
        Restaurant.query.filter_by(is_verified=True)
        .order_by(Restaurant.id.desc())
        .limit(6)
        .all()
    )
    return render_template('public/index.html', restaurants=restaurants)


@public_bp.route('/restaurant/<int:restaurant_id>')
def restaurant_detail(restaurant_id):
    """Restaurant detail page with menu"""
    restaurant = Restaurant.query.get(restaurant_id)

    if not restaurant:
        return render_template(
            'public/error.html',
            error="Restaurant not found"
        ), 404

    menus = Menu.query.filter_by(restaurant_id=restaurant_id).all()

    return render_template(
        'public/restaurant_detail.html',
        restaurant=restaurant,
        menus=menus
    )


@public_bp.route('/terms')
def terms():
    return render_template('public/terms.html')



@public_bp.route('/privacy')
def privacy():
    return render_template('public/privacy.html')


@public_bp.route('/about')
def about():
    """About page"""
    return render_template('public/about.html')



@public_bp.route('/contact')
def contact():
    return render_template('public/contact.html')


@public_bp.route('/restaurants')
def restaurants():
    """List all verified restaurants"""
    restaurants = (
        Restaurant.query.filter_by(is_verified=True)
        .order_by(Restaurant.name.asc())
        .all()
    )
    return render_template('public/restaurants.html', restaurants=restaurants)


@public_bp.route('/search')
def search():
    """Search restaurants by name, description, city, or cuisine"""
    query = request.args.get('q', '').strip()
    city = request.args.get('city', '').strip()
    cuisine = request.args.get('cuisine', '').strip()

    restaurants_query = Restaurant.query.filter_by(is_verified=True)

    if query:
        restaurants_query = restaurants_query.filter(
            (Restaurant.name.ilike(f"%{query}%")) |
            (Restaurant.description.ilike(f"%{query}%"))
        )

    if city:
        restaurants_query = restaurants_query.filter(
            Restaurant.city.ilike(city)
        )

    if cuisine:
        restaurants_query = restaurants_query.filter(
            Restaurant.cuisine.ilike(cuisine)
        )

    restaurants = restaurants_query.all()

    return render_template(
        'public/search_results.html',
        restaurants=restaurants,
        query=query,
        city=city,
        cuisine=cuisine
    )
