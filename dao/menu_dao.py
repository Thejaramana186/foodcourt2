from db import db
from models.menu import Menu
from models.restaurant import Restaurant
from sqlalchemy import and_, or_, desc
from datetime import datetime


class MenuDAO:
    def create_menu(self, menu):
        try:
            db.session.add(menu)
            db.session.commit()
            return menu
        except Exception as e:
            db.session.rollback()
            print(f"Error creating menu: {e}")
            return None
    
    def get_menu_by_id(self, menu_id):
        return Menu.query.get(menu_id)
    
    def get_menu_by_restaurant(self, restaurant_id, category='', type_filter='', page=None, per_page=None):
        query = Menu.query.filter(
            and_(
                Menu.restaurant_id == restaurant_id,
                Menu.is_available == True
            )
        )
        
        if category:
            query = query.filter_by(category=category)
        
        if type_filter:
            query = query.filter_by(type=type_filter)
        
        query = query.order_by(Menu.sort_order, Menu.category, Menu.name)
        
        if page and per_page:
            return query.paginate(page=page, per_page=per_page, error_out=False)
        else:
            return query.all()
    
    def get_categories_by_restaurant(self, restaurant_id):
        categories = db.session.query(Menu.category).filter(
            and_(
                Menu.restaurant_id == restaurant_id,
                Menu.is_available == True
            )
        ).distinct().all()
        return [category[0] for category in categories if category[0]]
    
    def update_menu(self, menu_item):
        try:
            menu_item.updated_at = datetime.utcnow()
            db.session.commit()
            return menu_item
        except Exception as e:
            db.session.rollback()
            print(f"Error updating menu: {e}")
            return None
    
    def delete_menu(self, menu_item):
        try:
        # If we received a Menu object, use it directly
          if isinstance(menu_item, Menu):
            menu = menu_item
          else:
            menu = Menu.query.get(menu_item)  # assume it's an ID

          if menu:
            menu.is_available = False   # soft delete
            db.session.commit()
            return True
          return False
        except Exception as e:
         db.session.rollback()
        print(f"Error deleting menu: {e}")
        return False

    
    def search_menu_items(self, search_term, page=1, per_page=20):
        query = Menu.query.join(Restaurant).filter(
            and_(
                Menu.is_available == True,
                Restaurant.is_active == True,
                Restaurant.is_verified == True,
                or_(
                    Menu.name.ilike(f'%{search_term}%'),
                    Menu.description.ilike(f'%{search_term}%'),
                    Menu.ingredients.ilike(f'%{search_term}%')
                )
            )
        )
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    def get_featured_menu_items(self, limit=12):
        return Menu.query.filter(
            and_(
                Menu.is_available == True,
                Menu.is_featured == True
            )
        ).join(Restaurant).filter(
            and_(
                Restaurant.is_active == True,
                Restaurant.is_verified == True
            )
        ).order_by(desc(Menu.created_at)).limit(limit).all()
    
    def get_menu_items_by_owner(self, owner_id, page=1, per_page=20):
        query = Menu.query.join(Restaurant).filter(
            Restaurant.owner_id == owner_id
        ).order_by(desc(Menu.created_at))
        
        return query.paginate(page=page, per_page=per_page, error_out=False)