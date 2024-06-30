# my_flask_app/app/routes.py

from flask import jsonify, Blueprint, render_template, redirect, url_for, request, session, flash, send_file, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import timedelta
import os
from app import db
from app.models import User, Content, ShopItem, ShopUser
from app.forms import ContentForm, AdminSignupForm, AdminLoginForm, ShopItemForm, AddToCartForm, ShopUserRegistrationForm, ShopUserLoginForm
from flask_login import login_user, logout_user, current_user
from app.decorators import login_required_admin, login_required_shop

# Create a Blueprint object for routes
bp = Blueprint('routes', __name__)

# Route for registering admin users
@bp.route('/admin/register', methods=['GET', 'POST'])
def register():
    
    form = AdminSignupForm()
    
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()      
        flash('User registered successfully!', 'success')
        return redirect(url_for('routes.admin_login'))
    else:
        print(form.errors)

    return render_template('admin/register.html', form=form)

# Route for admin login
@bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and isinstance(current_user._get_current_object(), User):
        return redirect(url_for('routes.admin_dashboard'))
    
    form = AdminLoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('routes.admin_login'))
        
        login_user(user, remember=form.remember_me.data)
        
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('routes.admin_dashboard'))
    
    return render_template('admin_login.html', form=form)

# Route for shop sign in
@bp.route('/login_shop', methods=['GET', 'POST'])
def login_shop():
    if current_user.is_authenticated and isinstance(current_user._get_current_object(), ShopUser):
        return redirect(url_for('routes.shop'))
    form = ShopUserLoginForm()
    
    if form.validate_on_submit():
        user = ShopUser.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('routes.login_shop'))
        login_user(user, remember=form.remember_me.data)
        
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('routes.shop'))
    
    return render_template('login_shop.html', form=form)

# Route for shop user registration
@bp.route('/register_shop', methods=['GET', 'POST'])
def register_shop():
    if current_user.is_authenticated:
        return redirect(url_for('routes.shop'))
    
    form = ShopUserRegistrationForm()
    if form.validate_on_submit():
        username=form.username.data 
        email=form.email.data
        password=form.password.data
        
        # Check is username already exists
        existing_user = ShopUser.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username!')
            return redirect(url_for('routes.register_shop'))
        
        # Check if eail already exits
        existing_email = ShopUser.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already exists. Please choose a different email.')
            return redirect(url_for('routes.register_shop'))
        
        # Create new shop user
        new_user = ShopUser(username=username, email=email, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('routes.login_shop'))
    
    return render_template('register_shop.html', form=form)

# Route for admin dashboard
@bp.route('/admin/dashboard', methods=['GET', 'POST'])
@login_required_admin
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('routes.admin_login'))
    return render_template('admin_dashboard.html')

# Route for creating new Posts
@bp.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if not session.get('admin_logged_in'):
        return redirect(url_for('routes.admin/login'))
    
    form = ContentForm()
    
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        author = form.author.data
        
        filename = None
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                filename = secure_filename(image.filename)
                image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        
        new_content = Content(title=title, body=body, image_filename=filename, author=author)
        db.session.add(new_content)
        db.session.commit()
    
        flash('Post created successfully', 'success')
        return redirect(url_for('routes.admin_dashboard'))
    
    else:
        # Log form validation errors
        print(f"Form validation failed: {form.errors}")
        print(f"Form data: {form.data}")
    
    contents = Content.query.all()
    
    # Include TinyMCE initialization parameters as context variables
    tiny_mce_config = {
        'selector': 'textarea#body',
        'plugins': 'advlist autolink lists link image charmap print preview anchor',
        'toolbar': 'undo redo | formatselect | bold italic backcolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image',
        'toolbar_mode': 'floating',
        'tinycomments_mode': 'embedded',
        'tinycomments_author': 'Author name',
    }
    
    return render_template('create_post.html', form=form, contents=contents, tiny_mce_config=tiny_mce_config)

# Display all content that exists for edit route. 
@bp.route('/admin/edit_content_list')
def edit_content_list():
    if not session.get('admin_logged_in'):
        return redirect(url_for('routes.admin_login'))
    form = ContentForm()
    contents = Content.query.all()
    return render_template('edit_content_list.html', form=form, contents=contents)

# Route for editing content
@bp.route('/admin/edit_content/<int:content_id>', methods=['GET', 'POST'])
def edit_content(content_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('routes.admin/login'))

    form = ContentForm()
    content = db.session.get(Content, content_id)

    if form.validate_on_submit():
        content.title = form.title.data
        content.body = form.body.data

        image = form.image.data
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            content.image_filename = filename

        db.session.commit()

        flash('Content updated successfully', 'success')
        return redirect(url_for('routes.admin_dashboard'))

    if content:
        form.title.data = content.title
        form.body.data = content.body

        # Include TinyMCE initialization parameters as context variables
        tiny_mce_config = {
            'selector': 'textarea#body',
            'plugins': 'advlist autolink lists link image charmap print preview anchor',
            'toolbar': 'undo redo | formatselect | bold italic backcolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image',
            'toolbar_mode': 'floating',
            'tinycomments_mode': 'embedded',
            'tinycomments_author': 'Author name',
        }

        return render_template('edit_content.html', form=form, content_id=content_id, tiny_mce_config=tiny_mce_config)
    else:
        flash('Content not found', 'Danger!')
        return redirect(url_for('routes.admin'))

# Route for deleting content
@bp.route('/admin/delete_content/<int:content_id>', methods=['POST'])
def delete_content(content_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('routes.admin/login'))

    content = Content.query.get_or_404(content_id)
    db.session.delete(content)
    db.session.commit()
    flash('Post deleted successfully', 'success')
    return redirect(url_for('routes.edit_content_list'))

# Route for deleting a post
@bp.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = Content.query.get_or_404(post_id)
    if post.image_filename:
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], post.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully', 'success')
    return redirect(url_for('routes.admin_dashboard'))

# Route for displaying the homepage
@bp.route('/')
def index():
    return render_template('index.html')

# Route to manage shop
@bp.route('/admin/manage_shop', methods=['GET', 'POST'])
def manage_shop():
    items = ShopItem.query.all()
    return render_template('manage_shop.html', items=items)

# Route to add shop items
@bp.route('/admin/add_shop_items', methods=['GET', 'POST'])
def add_shop_items():
    form = ShopItemForm()
    if form.validate_on_submit():
        image_file=form.image.data
        image_filename = image_file.filename
        image_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename))
        
        new_item = ShopItem(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            image_filename=image_filename
        )
        db.session.add(new_item)
        db.session.commit()
        flash('Shop item added successfully!', 'success')
        return redirect(url_for('routes.manage_shop'))
    return render_template('add_shop_items.html', form=form)

# Route to edit shop items
@bp.route('/admin/shop/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_shop_item(item_id):
    item = ShopItem.query.get_or_404(item_id)
    form = ShopItemForm(obj=item)
    if form.validate_on_submit():
        item.name = form.name.data
        item.description = form.description.data
        item.price = form.price.data
        if form.image.data:
            image_file = form.image.data
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            item.image_filename = filename
        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('routes.manage_shop'))
    return render_template('edit_shop_item.html', form=form, item=item)

# Route for deleting shop items
@bp.route('/admin/delete_shop_item/<int:item_id>', methods=['POST'])
def delete_shop_item(item_id):
    item =ShopItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Shop item deleted successfully!', 'sucess')
    return redirect(url_for('routes.manage_shop'))

# Route to display shop to users
@bp.route('/shop')
@login_required_shop
def shop():
    items= ShopItem.query.all()
    form = AddToCartForm()
    print("Form fields:", form.quantity)
    return render_template('shop.html', items=items, form=form)

# Roue for add items to cart
@bp.route('/add_to_cart/<int:item_id>', methods=['GET', 'POST'])
@login_required_shop
def add_to_cart(item_id):
    form = AddToCartForm()
    if form.validate_on_submit():
        quantity = form.quantity.data
        item = ShopItem.query.get(item_id)
    
        if item is None:
            flash('Item not found', 'danger')
            return redirect(url_for('routes.shop'))
        
        cart_item = {
            'item': item.to_dict(),
            'quantity': quantity
        }
        
        cart = session.get('cart', [])
        cart.append(cart_item)
        session['cart'] = cart
        
        flash(f"Added {quantity} of {item.name} to cart!", 'success')
        return redirect(url_for('routes.shop'))
    
    flash('Error adding to cart', 'danger')
    return redirect(url_for('routes.shop'))

# Route to cart
@bp.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    total_quantity = sum(item['quantity'] for item in cart_items)
    total_cost = sum(item['item']['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_quantity=total_quantity, total_cost=total_cost)

# Route to checkout
@bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        # Here you would process the payment
        flash('Payment successful!', 'success')
        session.pop('cart', None)
        return redirect(url_for('routes.shop'))
    cart_items = session.get('cart', [])
    total_quantity = sum(item['quantity'] for item in cart_items)
    total_cost = sum(item['item']['price'] * item['quantity'] for item in cart_items)
    return render_template('checkout.html', cart_items=cart_items, total_quantity=total_quantity, total_cost=total_cost)

# Route for PDF menu download
@bp.route('/menu')
def download_menu():
    # Assuming your PDF menu file is located in the static folder
    menu_path = 'static/pikngo_menu.pdf'
    # Provide a filename for the downloaded file (optional)
    filename = 'pikngo_menu.pdf'
    # Send the file to the user for download
    return send_file(menu_path, as_attachment=True)

# Route for displaying a single post
@bp.route('/post/<int:post_id>')
def post(post_id):
    post = Content.query.get(post_id)
    if post:
        return render_template('post.html', post=post)
    else:
        flash('Post not found', 'danger')
        return redirect(url_for('routes.index'))

# Route for displaying earlier posts
@bp.route('/earlier_posts')
def earlier_posts():
    posts = Content.query.order_by(Content.created_at.desc()).all()
    return render_template('earlier_posts.html', posts=posts)

# Route to log out
@bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('routes.index'))