# my_flask_app/app/__init__.py

from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Initialize SQLAlchemy and Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'routes.login_shop'
login_manager.login_view = 'routes.admin_login'

@login_manager.user_loader
def load_user(user_id):
    from app.models import User, ShopUser
    print(f"Loading user with ID {user_id} from path {request.path}")   
    if 'shop' in request.path:
        return ShopUser.query.get(int(user_id))
    elif 'admin' in request.path:
        return User.query.get(int(user_id))
    else:
        return None

# Register Blueprints
from app.routes import bp as routes_bp
app.register_blueprint(routes_bp)

# Import routes and models
from app import routes, models

# Initialize the database
def init_db():
    with app.app_context():
        db.create_all()

