from wtforms import Form, BooleanField, StringField, IntegerField ,PasswordField, validators, SubmitField
from wtforms.validators import regexp, InputRequired
from flask_wtf import FlaskForm


class RegistrationForm(FlaskForm):
    name = StringField('Name :', [validators.DataRequired(),validators.Length(min=2, max=25)])
    username = StringField('Username :', [validators.DataRequired(),validators.Length(min=8, max=19)])
    email = StringField('Email :', [validators.Length(min=12, max=35), validators.Email()])
    password = PasswordField('New Password :', [
        validators.DataRequired(), 
        validators.EqualTo('confirm', message='PASSWORD MUST MATCH!!')])
    confirm = PasswordField('Repat Password :')
    
class LoginForm(FlaskForm):
    email = StringField('Email :', [validators.Length(min=12, max=35), validators.Email()])
    password = PasswordField('Password :', [validators.DataRequired()])
    
    
    
# class LettersOnly(FlaskForm):
#     name = StringField('PLEASE ENTER LETTERS ONLY!!', validators=[InputRequired(), regexp('^[A-Za-z]+$', message="Only letters are allowed")])
    


