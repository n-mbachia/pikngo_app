# my_flask_app/app/routes.py

from flask import Blueprint, render_template, redirect, url_for, request, session, flash, send_file, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import timedelta
import os
from app import db
from app.models import User, Content
from app.forms import ContentForm, AdminSignupForm, AdminLoginForm

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

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already exists. Please use a different email.', 'error')
            return redirect(url_for('routes.register'))

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
    form = AdminLoginForm
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember_me = request.form.get('remember_me')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['admin_logged_in'] = True
            flash('Logged in successfully', 'success')

            if remember_me:
                session.permanent = True
                current_app.permanent_session_lifetime = timedelta(days=90)

            return redirect(url_for('routes.admin_dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('admin/login.html')

# Route for admin dashboard
@bp.route('/admin/dashboard', methods=['GET', 'POST'])
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
    posts = Content.query.all()
    return render_template('edit_content_list.html', posts=posts)

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
    return redirect(url_for('routes.admin_dashboard'))

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
