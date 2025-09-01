from flask_sqlalchemy import SQLAlchemy

# Create db instance here so it can be imported everywhere
db = SQLAlchemy()

# Import models after db is defined
from .cart import Cart
from .menu import Menu
from .user import User

__all__ = ['db', 'Cart', 'Menu', 'User']
