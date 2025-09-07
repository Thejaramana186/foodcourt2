import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-super-secret-key-change-in-production'
    
    # Database (use instance folder for SQLite)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'fooddelivery_auth.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True
    }
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'foodhub:'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    
    # Upload configuration
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Mail configuration (for future use)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Pagination
    ITEMS_PER_PAGE = 12
    ORDERS_PER_PAGE = 20
    USERS_PER_PAGE = 25
    
    # Business settings
    TAX_RATE = 0.05  # 5% tax
    DEFAULT_DELIVERY_TIME = 45  # minutes
    MAX_DELIVERY_DISTANCE = 10  # km
    
    # Role permissions
    ROLE_PERMISSIONS = {
        'customer': ['order', 'cart', 'profile'],
        'restaurant_owner': ['restaurant_management', 'menu_management', 'order_management'],
        'delivery_person': ['delivery_management', 'earnings'],
        'admin': ['user_management', 'restaurant_approval', 'system_analytics']
    }
