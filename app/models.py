from itsdangerous import URLSafeTimedSerializer as Serializer
from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager, app
from flask import current_app

@login_manager.user_loader
def load_user(user_id):
    user = db.session.get(User, int(user_id))
    if user and user.is_banned:
        return None # User is banned, do not load
    return user


# Association table for the many-to-many relationship between orders and products

order_product_association = db.Table(
    'order_product_association',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('quantity', db.Integer, default=1, nullable=False)
)

class User(db.Model, UserMixin):
    """
    User model for storing user information and handling authentication.
    """
    
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(25), nullable=False)
    lname = db.Column(db.String(25), nullable=False)
    username = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(125), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    gender = db.Column(db.String(10), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    home_address = db.Column(db.Text, nullable=True)
    image_file = db.Column(db.String(20), nullable=False, default="default.png")
    bio = db.Column(db.Text, nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_banned = db.Column(db.Boolean, default=False, nullable=False)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)

    # Relationships
    # 'backref' creates a 'customer' attribute on the Order model
    orders = db.relationship('Order', backref='customer', lazy=True, cascade="all, delete-orphan")
    cart = db.relationship('Cart', backref='user', uselist=False, cascade="all, delete-orphan")
    reviews = db.relationship('Review', backref='author', lazy=True, cascade="all, delete-orphan")
    uploaded_products = db.relationship('Product', backref='uploader', lazy=True, cascade="all, delete-orphan")


    def get_reset_token(self):
        """
        Generates a secure, timed token for password reset.
        """
        s = Serializer(app.config['SECRET_KEY'], salt='pw-reset')
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token, age=3600):
        """
        Verifies a password reset token and returns the user if valid.
        """
        s = Serializer(app.config['SECRET_KEY'], salt='pw-reset')
        try:
            user_id = s.loads(token, max_age=age)['user_id']
        except:
            return None
        return db.session.get(User, user_id)

    def __repr__(self):
        """
        Returns a string representation of the User object.
        """
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Product(db.Model):
    """
    Product model for e-commerce products.
    """
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    image_file = db.Column(db.String(200), nullable=True, default='default.png')
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    # Relationships
    # 'back_populates' links this relationship to the one on the Order model
    
    orders = db.relationship('OrderProduct', back_populates='product', cascade="all, delete-orphan", passive_deletes=True)
    reviews = db.relationship('Review', backref='product', lazy=True, cascade="all, delete-orphan")
    category = db.relationship('Category', back_populates='products')
    

class Category(db.Model):
    """
    Category model to categorize products.
    """
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Relationships
    products = db.relationship('Product', back_populates='category', lazy=True)

class Order(db.Model):
    """
    Order model to track customer purchases.
    """
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    
    status = db.Column(db.String(20), default='Pending', nullable=False)

    # Relationships
    # 'back_populates' links this relationship to the one on the Product model
    
    products = db.relationship('OrderProduct', back_populates='order', cascade="all, delete-orphan", passive_deletes=True)

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade="all, delete-orphan")

class CartItem(db.Model):
    __tablename__ = 'cart_item'
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    product = db.relationship('Product', backref='cart_items')

class OrderProduct(db.Model):
    __tablename__ = 'order_product'
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
    quantity = db.Column(db.Integer, default=1, nullable=False)

    order = db.relationship('Order', back_populates='products')
    product = db.relationship('Product', back_populates='orders')
# New model for Reviews
class Review(db.Model):
    """
    Review model for storing customer reviews.
    """
    __tablename__ = 'review'
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def __repr__(self):
        return f"Review('{self.rating}', '{self.text}')"

# New model for Newsletter subscriptions
class Newsletter(db.Model):
    """
    Newsletter model for storing subscriber emails.
    """
    __tablename__ = 'newsletter'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subscription_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        """
        Returns a string representation of the Newsletter object.
        """
        return f"Newsletter('{self.email}')"