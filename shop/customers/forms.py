from wtforms import Form, StringField, TextAreaField, PasswordField, SubmitField, validators, ValidationError
from flask_wtf.file import FileRequired, FileAllowed, FileField
from flask_wtf import FlaskForm
from .models import Register

class CustomerRegisterForm(FlaskForm):
    name = StringField('Name: ')
    username = StringField('Username: ', [validators.DataRequired()])
    email = StringField('Email: ', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password: ', validators=[validators.DataRequired(), validators.EqualTo('confirm', message=' Both password must match! ')])
    confirm = PasswordField('Repeat Password: ', [validators.DataRequired()])
    
    state = StringField('State: ', [validators.DataRequired()])
    city = StringField('City: ', [validators.DataRequired()])
    contact = StringField('Contact: ', [validators.DataRequired()])
    address = StringField('Address: ', [validators.DataRequired()])
    zipcode = StringField('Zip code: ', [validators.DataRequired()])
    
    profile = FileField('Profile', validators=[FileAllowed(['jpg','png','jpeg'], 'Image only please')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        if Register.query.filter_by(username=username.data).first():
            raise ValidationError("This username is already in use!")
        
    def validate_email(self, email):
        if Register.query.filter_by(email=email.data).first():
            raise ValidationError("This email address is already in use!")
        
class CustomerLoginForm(FlaskForm):
    email = StringField('Email: ', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password: ', [validators.DataRequired()])
    
    
    
class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[validators.DataRequired(), validators.Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = Register.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')
        
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[validators.DataRequired()])
    confirm = PasswordField('Confirm Password',
                                     validators=[validators.DataRequired(),validators.EqualTo('password')])
    submit = SubmitField('Reset Password')