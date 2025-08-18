from db import db
from datetime import datetime

class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    cuisine = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Float, default=0.0)
    delivery_time = db.Column(db.String(20), nullable=True)
    image = db.Column(db.String(200), nullable=True)
    cover_image = db.Column(db.String(200), nullable=True)
    type = db.Column(db.String(20), nullable=False, default='both')  # veg, non-veg, both
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    opening_time = db.Column(db.String(10), nullable=True)
    closing_time = db.Column(db.String(10), nullable=True)
    delivery_fee = db.Column(db.Float, default=0.0)
    minimum_order = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    menus = db.relationship('Menu', backref='restaurant', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='restaurant', lazy=True)
    
    def get_average_rating(self):
        """Calculate average rating from orders"""
        from models.order import Order
        orders = Order.query.filter_by(restaurant_id=self.id, status='delivered').all()
        if not orders:
            return 0.0
        ratings = [order.rating for order in orders if order.rating]
        return sum(ratings) / len(ratings) if ratings else 0.0
    
    def get_total_orders(self):
        """Get total number of orders"""
        from models.order import Order
        return Order.query.filter_by(restaurant_id=self.id).count()
    
    def get_revenue(self):
        """Calculate total revenue"""
        from models.order import Order
        orders = Order.query.filter_by(restaurant_id=self.id, status='delivered').all()
        return sum(order.total_amount for order in orders)
    
    def is_open(self):
        """Check if restaurant is currently open"""
        if not self.opening_time or not self.closing_time:
            return True
        
        from datetime import datetime, time
        now = datetime.now().time()
        opening = datetime.strptime(self.opening_time, '%H:%M').time()
        closing = datetime.strptime(self.closing_time, '%H:%M').time()
        
        if opening <= closing:
            return opening <= now <= closing
        else:  # Overnight hours
            return now >= opening or now <= closing
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'cuisine': self.cuisine,
            'rating': self.rating,
            'delivery_time': self.delivery_time,
            'image': self.image,
            'cover_image': self.cover_image,
            'type': self.type,
            'address': self.address,
            'city': self.city,
            'phone': self.phone,
            'email': self.email,
            'opening_time': self.opening_time,
            'closing_time': self.closing_time,
            'delivery_fee': self.delivery_fee,
            'minimum_order': self.minimum_order,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Restaurant {self.name}>'