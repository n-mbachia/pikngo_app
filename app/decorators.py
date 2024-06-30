# my_flask_app/app/decorators.py

from functools import wraps
from flask import redirect, url_for, request
from flask_login import current_user

def login_required_shop(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('routes.login_shop', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def login_required_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwags):
        if not current_user.is_authenticated:
            return redirect(url_for('routes.admin_login', next=request.url))
        return f(*args, **kwags)
    return decorated_function