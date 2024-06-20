# my_flask_app/app/forms.py

from flask_wtf import FlaskForm
from wtforms import IntegerField, HiddenField, StringField, BooleanField, PasswordField, SubmitField, TextAreaField, FloatField, FileField, ValidationError
from wtforms.validators import DataRequired, NumberRange, Email, Length, ValidationError, EqualTo
from flask_wtf.file import FileField, FileAllowed, FileSize
from app.models import User

class AdminSignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken.')
        
    def validate_email(self, email):
        user=User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered.')
    
class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ContentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=255)])
    body = TextAreaField('Body', validators=[DataRequired()])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif']), FileSize(max_size=2 * 1024 * 1024)])
    author = StringField('Author', validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField('Submit')

# createforms for adding and editing shop items
class ShopItemForm(FlaskForm):
    name = StringField('Item name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif']), FileSize(max_size=2 * 1024 * 1024)])
    submit = SubmitField('Upload Shop Item')
    
class AddToCartForm(FlaskForm):
    item_id = HiddenField('Item ID', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add to Cart')
    
# For for shop user registratio
class ShopUserRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
        
# create for fror shop user login
class ShopUserLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')