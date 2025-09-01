from db import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(50), nullable=True)
    role = db.Column(
        db.String(20), 
        nullable=False, 
        default='customer'  # customer, restaurant_owner, delivery_person, admin
    )
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    carts = db.relationship(
        'Cart', backref='user', lazy=True, cascade='all, delete-orphan'
    )

    # Orders placed by this user (as a customer)
    customer_orders = db.relationship(
        "Order",
        foreign_keys="Order.customer_id",
        back_populates="customer",
        
    )

    # Orders delivered by this user (as a delivery person)
    delivery_orders = db.relationship(
        "Order",
        foreign_keys="Order.delivery_person_id",
        back_populates="delivery_person",
        
    )


    
    # Restaurants owned by this user
    restaurants = db.relationship('Restaurant', backref='owner', lazy=True)
    
    # Flask-Login required methods (UserMixin provides defaults, but we can override)
    def get_id(self):
        return str(self.id)
    
    def is_authenticated(self):
        return True
    
    def is_active_user(self):
        return self.is_active
    
    def is_anonymous(self):
        return False
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def is_customer(self):
        return self.role == 'customer'
    
    def is_restaurant_owner(self):
        return self.role == 'restaurant_owner'
    
    def is_delivery_person(self):
        return self.role == 'delivery_person'
    
    def is_admin(self):
        return self.role == 'admin'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.name} ({self.role})>'
