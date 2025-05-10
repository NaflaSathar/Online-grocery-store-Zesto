from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from decimal import Decimal

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(255), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='user', lazy=True)

    def get_total_spent(self):
        return sum(order.total_amount for order in self.orders)

    def get_recent_orders_count(self):
        return Order.query.filter_by(user_id=self.id).count()

class Product(db.Model):
    __tablename__ = 'products'
    product_id = db.Column(db.Integer, primary_key=True)
    product_key = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    stock_quantity = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_per_unit = db.Column(db.Numeric(10, 2), nullable=False)

# Create tables (run once)
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper functions
def get_cart_count():
    cart = session.get('cart', {})
    return sum(item['quantity'] for item in cart.values())

@app.context_processor
def inject_cart_count():
    return dict(cart_count=get_cart_count())

def init_products():
    """Initialize products if database is empty"""
    if Product.query.count() == 0:
        products = [
            {'product_key': 'oranges', 'name': 'Oranges', 'price': 80, 'category': 'Fruits', 'image_path': 'images/oranges.jpg'},
            {'product_key': 'grapes', 'name': 'Grapes', 'price': 90, 'category': 'Fruits', 'image_path': 'images/grapes.jpg'},
            {'product_key': 'poha', 'name': 'Poha', 'price': 35, 'category': 'Grains', 'image_path': 'images/poha.jpg'},
            {'product_key': 'bread', 'name': 'Whole Wheat Bread', 'price': 40, 'category': 'Bakery', 'image_path': 'images/bread.jpg'},
            {'product_key': 'milk', 'name': 'Organic Milk', 'price': 60, 'category': 'Dairy', 'image_path': 'images/milk.jpg'},
            {'product_key': 'eggs', 'name': 'Eggs (12 pcs)', 'price': 70, 'category': 'Dairy', 'image_path': 'images/eggs.jpg'},
            {'product_key': 'rice', 'name': 'Basmati Rice (1kg)', 'price': 120, 'category': 'Grains', 'image_path': 'images/rice.jpg'},
            {'product_key': 'toor_dal', 'name': 'Toor Dal (1kg)', 'price': 100, 'category': 'Grains', 'image_path': 'images/toor_dal.jpg'},
            {'product_key': 'tomatoes', 'name': 'Tomatoes (1kg)', 'price': 30, 'category': 'Vegetables', 'image_path': 'images/tomatoes.jpg'},
            {'product_key': 'onions', 'name': 'Onions (1kg)', 'price': 25, 'category': 'Vegetables', 'image_path': 'images/onions.jpg'}
        ]
        for prod in products:
            product = Product(**prod)
            db.session.add(product)
        db.session.commit()

# Initialize products on first run
with app.app_context():
    init_products()

# Routes
@app.route('/')
def index():
    category = request.args.get('category')
    query = Product.query
    
    if category:
        products_list = query.filter_by(category=category).all()
    else:
        products_list = query.all()
    
    products_dict = {p.product_key: {
        'name': p.name,
        'price': float(p.price),
        'image': p.image_path,
        'category': p.category
    } for p in products_list}
    
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories]

    # Get user stats if logged in
    user_stats = {}
    if current_user.is_authenticated:
        user_stats = {
            'recent_orders_count': current_user.get_recent_orders_count(),
            'total_spent': float(current_user.get_total_spent())
        }
    
    return render_template('index.html', 
                         products=products_dict, 
                         categories=categories, 
                         selected_category=category,
                         **user_stats)

@app.route('/add/<item>')
def add_to_cart(item):
    product = Product.query.filter_by(product_key=item).first()
    if not product:
        flash('Product not found!', 'error')
        return redirect(url_for('index'))
    
    cart = session.get('cart', {})
    if item in cart:
        cart[item]['quantity'] += 1
    else:
        cart[item] = {
            'name': product.name,
            'price': float(product.price),
            'quantity': 1
        }
    session['cart'] = cart
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render_template('cart.html', cart=cart, total=total)

@app.route('/remove/<item>')
def remove(item):
    cart = session.get('cart', {})
    if item in cart:
        del cart[item]
        session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('index'))
    
    total = sum(item['price'] * item['quantity'] for item in cart.values())

    if request.method == 'POST':
        address = request.form.get('address')
        contact = request.form.get('contact')
        payment = request.form.get('payment')

        try:
            order = Order(
                user_id=current_user.id,
                total_amount=total,
                shipping_address=address,
                contact_number=contact,
                payment_method=payment
            )
            db.session.add(order)
            db.session.flush()
            
            for product_key, item in cart.items():
                product = Product.query.filter_by(product_key=product_key).first()
                if product:
                    order_item = OrderItem(
                        order_id=order.order_id,
                        product_id=product.product_id,
                        quantity=item['quantity'],
                        price_per_unit=item['price']
                    )
                    db.session.add(order_item)
            
            db.session.commit()
            session.pop('cart', None)
            flash('Order placed successfully!', 'success')
            return redirect(url_for('success'))
        except Exception as e:
            db.session.rollback()
            flash('Error processing your order. Please try again.', 'error')
            app.logger.error(f'Order processing error: {str(e)}')

    return render_template('checkout.html', cart=cart, total=total)

@app.route('/success')
@login_required
def success():
    return render_template('success.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        new_address = request.form.get('address', '').strip()
        if new_address:
            current_user.address = new_address
            db.session.commit()
            flash('Address updated successfully!', 'success')
        else:
            flash('Address cannot be empty.', 'error')
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('profile.html', 
                         user=current_user,
                         orders=user_orders)

@app.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=user_orders)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or len(username) < 3:
            flash('Username must be at least 3 characters long', 'error')
            return redirect(url_for('register'))
            
        if not email or '@' not in email:
            flash('Please enter a valid email address', 'error')
            return redirect(url_for('register'))
            
        if not password or len(password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return redirect(url_for('register'))
            
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email.', 'error')
            return redirect(url_for('register'))
        
        try:
            # Create new user
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, email=email, password_hash=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            
            flash('Account created successfully! Please login to continue.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating your account. Please try again.', 'error')
            app.logger.error(f'Registration error: {str(e)}')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            flash('Welcome back to Zesto!', 'success')
            
            # Get the next page from the query parameters, or default to index
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('index')
            return redirect(next_page)
        else:
            flash('Invalid username or password. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)