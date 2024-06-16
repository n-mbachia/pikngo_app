# my_flask_app/config.py

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_really_secure_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BLOGGING_SITENAME = 'Pik&Go'
    UPLOAD_FOLDER =os.path.join(basedir, 'app', 'static', 'uploads')
