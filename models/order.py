from db import db
from datetime import datetime


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Customer placing order
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    delivery_person_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Assigned delivery person

    # Order details
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    delivery_fee = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), nullable=False, default='pending')  
    # pending, confirmed, preparing, ready_for_pickup, out_for_delivery, delivered, cancelled
    
    # Customer details
    booking_name = db.Column(db.String(100), nullable=False)
    booking_email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_city = db.Column(db.String(50), nullable=True)
    delivery_pincode = db.Column(db.String(10), nullable=True)
    
    # Timing
    delivery_date = db.Column(db.Date, nullable=True)
    delivery_time = db.Column(db.String(20), nullable=True)
    estimated_delivery_time = db.Column(db.DateTime, nullable=True)
    actual_delivery_time = db.Column(db.DateTime, nullable=True)
    
    # Payment
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed, refunded
    transaction_id = db.Column(db.String(100), nullable=True)
    
    # Additional info
    special_instructions = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Integer, nullable=True)  # 1-5 stars
    review = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    prepared_at = db.Column(db.DateTime, nullable=True)
    pickup_at = db.Column(db.DateTime, nullable=True)
    delivered_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    order_items = db.relationship(
        'OrderItem',
        backref='order',
        lazy=True,
        cascade='all, delete-orphan'
    )

    # Link to User as customer
    customer = db.relationship(
        'User',
        backref=db.backref('orders', overlaps="customer_orders"),
        foreign_keys=[customer_id]
    )
    # Link to User as delivery person
    delivery_person = db.relationship(
        "User",
        foreign_keys=[delivery_person_id],
        back_populates="delivery_orders"
    )



    
    # Link to Restaurant
    restaurant = db.relationship("Restaurant", back_populates="orders", lazy=True)

    
    def __init__(self, **kwargs):
        super(Order, self).__init__(**kwargs)
        if not self.order_number:
            self.order_number = self.generate_order_number()
    
    def generate_order_number(self):
        """Generate unique order number"""
        import random
        import string
        timestamp = datetime.now().strftime('%Y%m%d')
        random_suffix = ''.join(random.choices(string.digits, k=4))
        return f"ORD{timestamp}{random_suffix}"
    
    def get_status_display(self):
        """Get user-friendly status display"""
        status_map = {
            'pending': 'Order Placed',
            'confirmed': 'Confirmed',
            'preparing': 'Being Prepared',
            'ready_for_pickup': 'Ready for Pickup',
            'out_for_delivery': 'Out for Delivery',
            'delivered': 'Delivered',
            'cancelled': 'Cancelled'
        }
        return status_map.get(self.status, self.status.title())
    
    def get_total_items(self):
        """Get total number of items in order"""
        return sum(item.quantity for item in self.order_items)
    
    def can_be_cancelled(self):
        """Check if order can be cancelled"""
        return self.status in ['pending', 'confirmed']
    
    def can_be_rated(self):
        """Check if order can be rated"""
        return self.status == 'delivered' and not self.rating
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'customer_id': self.customer_id,
            'restaurant_id': self.restaurant_id,
            'delivery_person_id': self.delivery_person_id,
            'total_amount': self.total_amount,
            'delivery_fee': self.delivery_fee,
            'discount_amount': self.discount_amount,
            'tax_amount': self.tax_amount,
            'status': self.status,
            'status_display': self.get_status_display(),
            'booking_name': self.booking_name,
            'booking_email': self.booking_email,
            'phone': self.phone,
            'delivery_address': self.delivery_address,
            'delivery_city': self.delivery_city,
            'delivery_pincode': self.delivery_pincode,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'delivery_time': self.delivery_time,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'special_instructions': self.special_instructions,
            'rating': self.rating,
            'review': self.review,
            'restaurant': self.restaurant.to_dict() if self.restaurant else None,
            'order_items': [item.to_dict() for item in self.order_items],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'estimated_delivery_time': self.estimated_delivery_time.isoformat() if self.estimated_delivery_time else None,
            'actual_delivery_time': self.actual_delivery_time.isoformat() if self.actual_delivery_time else None
        }
    
    def __repr__(self):
        return f'<Order {self.order_number}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Price at time of order
    customization = db.Column(db.Text, nullable=True)  # Special customization requests
    
    # Relationship
    menu = db.relationship('Menu', backref='order_items', lazy=True)
    
    def get_total_price(self):
        """Get total price for this item"""
        return self.price * self.quantity
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'menu_id': self.menu_id,
            'quantity': self.quantity,
            'price': self.price,
            'total_price': self.get_total_price(),
            'customization': self.customization,
            'menu': self.menu.to_dict() if self.menu else None
        }
    
    def __repr__(self):
        return f'<OrderItem {self.id}>'
