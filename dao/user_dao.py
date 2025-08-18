from db import db
from models.user import User
from sqlalchemy import or_, and_, func
from datetime import datetime, timedelta

class UserDAO:
    def create_user(self, user):
        try:
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            print(f"Error creating user: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        return User.query.get(user_id)
    
    def get_user_by_username(self, username):
        return User.query.filter_by(username=username).first()
    
    def get_user_by_email(self, email):
        return User.query.filter_by(email=email).first()
    
    def update_user(self, user):
        try:
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            print(f"Error updating user: {e}")
            return None
    
    def delete_user(self, user_id):
        try:
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting user: {e}")
            return False
    
    def get_all_users(self, page=1, per_page=10, role_filter='', search=''):
        query = User.query
        
        if role_filter:
            query = query.filter_by(role=role_filter)
        
        if search:
            query = query.filter(
                or_(
                    User.username.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%'),
                    User.first_name.ilike(f'%{search}%'),
                    User.last_name.ilike(f'%{search}%')
                )
            )
        
        return query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    def get_user_count(self):
        return User.query.count()
    
    def get_user_count_by_role(self, role):
        return User.query.filter_by(role=role).count()
    
    def get_recent_users(self, limit=10):
        return User.query.order_by(User.created_at.desc()).limit(limit).all()
    
    def get_user_growth_data(self, days=30):
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        growth_data = []
        current_date = start_date
        
        while current_date <= end_date:
            count = User.query.filter(
                and_(
                    User.created_at >= current_date,
                    User.created_at < current_date + timedelta(days=1)
                )
            ).count()
            
            growth_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'count': count
            })
            current_date += timedelta(days=1)
        
        return growth_data
    
    def search_users(self, search_term, page=1, per_page=10):
        query = User.query.filter(
            or_(
                User.username.ilike(f'%{search_term}%'),
                User.email.ilike(f'%{search_term}%'),
                User.first_name.ilike(f'%{search_term}%'),
                User.last_name.ilike(f'%{search_term}%')
            )
        )
        return query.paginate(page=page, per_page=per_page, error_out=False)