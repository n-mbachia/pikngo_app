# my_flask_app/app/__init_.py

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# csrf = CSRFProtect(app)

from app.routes import bp as routes_bp
app.register_blueprint(routes_bp)

from app import routes, models

# Initialize the database
def init_db():
    with app.app_context():
        db.create_all()