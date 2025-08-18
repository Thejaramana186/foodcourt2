from db import db
from datetime import datetime

class Menu(db.Model):
    __tablename__ = 'menus'
    
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    discounted_price = db.Column(db.Float, nullable=True)
    category = db.Column(db.String(50), nullable=True)
    type = db.Column(db.String(20), nullable=False, default='veg')  # veg, non-veg
    image = db.Column(db.String(200), nullable=True)
    ingredients = db.Column(db.Text, nullable=True)
    allergens = db.Column(db.String(200), nullable=True)
    spice_level = db.Column(db.String(20), nullable=True)  # mild, medium, hot, very_hot
    preparation_time = db.Column(db.Integer, nullable=True)  # in minutes
    calories = db.Column(db.Integer, nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_effective_price(self):
        """Get the price after discount if applicable"""
        return self.discounted_price if self.discounted_price else self.price
    
    def get_discount_percentage(self):
        """Calculate discount percentage"""
        if self.discounted_price and self.discounted_price < self.price:
            return int(((self.price - self.discounted_price) / self.price) * 100)
        return 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'restaurant_id': self.restaurant_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'discounted_price': self.discounted_price,
            'effective_price': self.get_effective_price(),
            'discount_percentage': self.get_discount_percentage(),
            'category': self.category,
            'type': self.type,
            'image': self.image,
            'ingredients': self.ingredients,
            'allergens': self.allergens,
            'spice_level': self.spice_level,
            'preparation_time': self.preparation_time,
            'calories': self.calories,
            'is_available': self.is_available,
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Menu {self.name}>'