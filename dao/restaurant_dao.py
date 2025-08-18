from db import db
from models.restaurant import Restaurant
from models.order import Order
from sqlalchemy import or_, and_, func, desc
from datetime import datetime, timedelta

class RestaurantDAO:
    def create_restaurant(self, restaurant):
        try:
            db.session.add(restaurant)
            db.session.commit()
            return restaurant
        except Exception as e:
            db.session.rollback()
            print(f"Error creating restaurant: {e}")
            return None
    
    def get_restaurant_by_id(self, restaurant_id):
        return Restaurant.query.get(restaurant_id)
    
    def get_restaurants(self, page=1, per_page=10, search='', cuisine='', type_filter='', sort_by='rating', verified_only=False):
        query = Restaurant.query.filter_by(is_active=True)
        
        if verified_only:
            query = query.filter_by(is_verified=True)
        
        if search:
            query = query.filter(
                or_(
                    Restaurant.name.ilike(f'%{search}%'),
                    Restaurant.cuisine.ilike(f'%{search}%'),
                    Restaurant.description.ilike(f'%{search}%')
                )
            )
        
        if cuisine:
            query = query.filter_by(cuisine=cuisine)
        
        if type_filter:
            if type_filter == 'veg':
                query = query.filter(Restaurant.type.in_(['veg', 'both']))
            elif type_filter == 'non-veg':
                query = query.filter(Restaurant.type.in_(['non-veg', 'both']))
        
        # Apply sorting
        if sort_by == 'rating':
            query = query.order_by(desc(Restaurant.rating))
        elif sort_by == 'delivery_time':
            query = query.order_by(Restaurant.delivery_time)
        elif sort_by == 'name':
            query = query.order_by(Restaurant.name)
        elif sort_by == 'newest':
            query = query.order_by(desc(Restaurant.created_at))
        
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    def get_restaurants_by_owner(self, owner_id, page=1, per_page=10):
        if page:
            return Restaurant.query.filter_by(owner_id=owner_id).order_by(desc(Restaurant.created_at)).paginate(
                page=page, per_page=per_page, error_out=False
            )
        else:
            return Restaurant.query.filter_by(owner_id=owner_id).order_by(desc(Restaurant.created_at)).all()
    
    def get_all_cuisines(self):
        cuisines = db.session.query(Restaurant.cuisine).distinct().all()
        return [cuisine[0] for cuisine in cuisines if cuisine[0]]
    
    def update_restaurant(self, restaurant):
        try:
            restaurant.updated_at = datetime.utcnow()
            db.session.commit()
            return restaurant
        except Exception as e:
            db.session.rollback()
            print(f"Error updating restaurant: {e}")
            return None
    
    def delete_restaurant(self, restaurant_id):
        try:
            restaurant = Restaurant.query.get(restaurant_id)
            if restaurant:
                restaurant.is_active = False
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting restaurant: {e}")
            return False
    
    def get_featured_restaurants(self, limit=6):
        return Restaurant.query.filter_by(is_active=True, is_verified=True).order_by(desc(Restaurant.rating)).limit(limit).all()
    
    def get_restaurant_count(self):
        return Restaurant.query.filter_by(is_active=True).count()
    
    def get_recent_restaurants(self, limit=10):
        return Restaurant.query.order_by(desc(Restaurant.created_at)).limit(limit).all()
    
    def get_all_restaurants_admin(self, page=1, per_page=20, search='', status_filter=''):
        query = Restaurant.query
        
        if search:
            query = query.filter(
                or_(
                    Restaurant.name.ilike(f'%{search}%'),
                    Restaurant.cuisine.ilike(f'%{search}%'),
                    Restaurant.city.ilike(f'%{search}%')
                )
            )
        
        if status_filter == 'active':
            query = query.filter_by(is_active=True)
        elif status_filter == 'inactive':
            query = query.filter_by(is_active=False)
        elif status_filter == 'verified':
            query = query.filter_by(is_verified=True)
        elif status_filter == 'unverified':
            query = query.filter_by(is_verified=False)
        
        return query.order_by(desc(Restaurant.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    def search_restaurants(self, search_term, page=1, per_page=12):
        query = Restaurant.query.filter(
            and_(
                Restaurant.is_active == True,
                Restaurant.is_verified == True,
                or_(
                    Restaurant.name.ilike(f'%{search_term}%'),
                    Restaurant.cuisine.ilike(f'%{search_term}%'),
                    Restaurant.description.ilike(f'%{search_term}%')
                )
            )
        )
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    def get_cuisine_popularity(self):
        """Get cuisine popularity based on order count"""
        results = db.session.query(
            Restaurant.cuisine,
            func.count(Order.id).label('order_count')
        ).join(Order).group_by(Restaurant.cuisine).order_by(desc('order_count')).limit(10).all()
        
        return [{'cuisine': result[0], 'count': result[1]} for result in results]
    
    def get_top_restaurants_by_revenue(self, limit=10):
        """Get top restaurants by revenue"""
        results = db.session.query(
            Restaurant,
            func.sum(Order.total_amount).label('revenue')
        ).join(Order).filter(Order.status == 'delivered').group_by(Restaurant.id).order_by(desc('revenue')).limit(limit).all()
        
        return [{'restaurant': result[0], 'revenue': result[1]} for result in results]