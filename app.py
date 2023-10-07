from flask import Flask, render_template, request, url_for, flash, redirect, session
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import os
import random


#Used to set up my database.
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

#This is where the products are stored.
class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    content = db.Column(db.String(500))
    image = db.Column(db.String(255))
    price = db.Column(db.Float)
    ecological_footprint = db.Column(db.String(50))

    def __repr__(self):
        return '<Title %r>' % self.title

#A list is used to store the user's cart.
cart =[]


#This ensures that the user's cart does not expire when the user closes their browser.
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def index():
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order', 'asc')
    cart = session.get('cart', [])
    cart_count = len(cart)

    # Get all products from the database.
    products = Product.query.all()

    # Sort the products based on the sort_by and sort_order arguments
    if sort_by == 'price':
        products = sorted(products, key=lambda x: x.price or float('inf'), reverse=sort_order == 'desc')
    elif sort_by == 'name':
        products = sorted(products, key=lambda x: x.title, reverse=sort_order == 'desc')

    # Determine if the table headings should be displayed ie no products to be displayed on the site.
    show_table_headings = bool(products)

    return render_template('index.html', products=products, sort_by=sort_by, sort_order=sort_order, cart_count=cart_count, show_table_headings=show_table_headings)


#Used to add products on the site.
@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        file = request.files['file']
        price = request.form.get('price')
        ecological_footprint = request.form.get('ecological_footprint')

        if not title:
            flash('Title is required!')
        elif not content:
            flash('Content is required!')
        elif not file:
            flash('Image is required!')
        elif not allowed_file(file.filename):
            flash('Invalid file extension! Allowed extensions are png, jpg, jpeg.')
        elif not price:
            flash('Price is required!')
        elif not is_valid_price(price):
            flash('Invalid price! Price must be a decimal value to 2 decimal places.')
        else:
            #Saves all the inputted product information.
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product = Product(
                title=title,
                content=content,
                image=filename,
                price=price,
                ecological_footprint=ecological_footprint
            )
            db.session.add(product)
            db.session.commit()
            flash('Product created successfully!')
            return redirect(url_for('index'))

    return render_template('create.html')

#Returns true if the file inputted is valid.
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Returns true if the inputted price is valid.
def is_valid_price(price):
    try:
        price = float(price)
        if price < 0 or round(price, 2) != price:
            return False
        return True
    except ValueError:
        return False

#Adds the products to the current user's basket.
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form['product_id']
    product = Product.query.filter_by(id=product_id).first()
    item = {
        'id': product.id,
        'title': product.title,
        'price': product.price,
    }

    cart = session.get('cart', [])
    for cart_item in cart:
        if cart_item['id'] == item['id']:
            flash('Product already added to cart!')
            return redirect('/')

    session['cart'] = cart + [item]
    flash('Product added to cart!')
    return redirect('/')

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    session['cart'] = []
    flash('Cart cleared')
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    cart_total = sum(float(item['price']) for item in cart)
    return render_template('cart.html', cart=cart, cart_total=cart_total)

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    title = request.form['item_title']
    cart = session.get('cart', [])
    for item in cart:
        if item['title'] == title:
            cart.remove(item)
            break
    session['cart'] = cart
    flash('Item removed from cart')
    return redirect(url_for('cart'))

@app.route('/checkout_cart')
def checkout_cart():
    return redirect(url_for('checkout'))

#Retrieves the cart data from the current session and calculates the the total price. A random token is used for added security, helping reduce CSRF attacks.
@app.route('/checkout')
def checkout():
    cart = session.get('cart', [])
    cart_total = sum(float(item['price']) for item in cart)
    token = ''.join(random.choice('0123456789abcdef') for i in range(64))
    return render_template('checkout.html', cart=cart, cart_total=cart_total, random=random, token=token)

#Deletes the product from the database so that other uses cannot buy the same product.
@app.route('/place_order')
def place_order():
    cart = session.get('cart', [])
    bought_items = []
    not_bought_items = []

    for item in cart:
        try:
            product = Product.query.filter_by(id=item['id']).first()
            db.session.delete(product)
            db.session.commit()
            bought_items.append(product.title)
        except:
            not_bought_items.append(item['title'])

    session['cart'] = []
    
    if bought_items:
        flash(f"Thank you for purchasing {', '.join(bought_items)}!")
    
    if not_bought_items:
        flash(f"The following items are now unavailable: {', '.join(not_bought_items)}")

    return redirect('/')

#Gets the product from the database and works out the number of items in the cart.
@app.route('/product/<int:id>')
def product(id):
    product = Product.query.get_or_404(id)
    cart = session.get('cart', [])
    cart_count = len(cart)  # get the number of items in the cart
    return render_template('product.html', product=product, cart_count=cart_count)

@app.route('/about')
def about():
    cart = session.get('cart', [])
    cart_count = len(cart)  # get the number of items in the cart
    return render_template('about.html', cart_count=cart_count)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)