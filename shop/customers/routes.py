from flask import render_template, session, request, redirect,url_for,flash,current_app
from shop import app,db,photos,bcrypt,login_manager, mail
from flask_login import login_required, current_user, login_user, logout_user
from .forms import CustomerRegisterForm , CustomerLoginForm, RequestResetForm, ResetPasswordForm
from .models import Register, CustomerOrder
import secrets
import os
from flask_mail import Message


@app.route('/customer/register', methods=['GET','POST'])
def customer_register():
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        register = Register(name=form.name.data, username=form.username.data, email=form.email.data,password=hash_password,city=form.city.data,contact=form.contact.data, address=form.address.data, zipcode=form.zipcode.data, token_used = 0)
        db.session.add(register)
        flash(f'Register Successful!', 'success')
        db.session.commit()
        return redirect(url_for('customerLogin'))
    return render_template('customer/register.html', form=form)

@app.route('/customer/login', methods=['GET', 'POST'])
def customerLogin():
    form = CustomerLoginForm()
    if form.validate_on_submit():
        user = Register.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        flash('Incorrect Email or Password', 'danger')
        return redirect(url_for('customerLogin'))
    return render_template('customer/login.html', form = form)

@app.route('/customer/logout')
def customer_logout():
    logout_user()
    return redirect(url_for('customerLogin'))

@app.route('/order')
def get_order():
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        try:
            order = CustomerOrder(invoice=invoice,customer_id=customer_id,orders=session['ShoppingCart'])
            db.session.add(order)
            flash('Your order has been sent!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            print(e)
            flash('Error getting your order', 'danger')
            return redirect(url_for('getCart'))
        
        
def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', 
                  sender = "hardwellapollo1029@yahoo.com",
                  recipients=[user.email])
    msg.body = f''' To reset your password, visit the following link:
    {url_for('reset_token', token = token, _external=True)}
    If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)
    pass

@app.route("/customer/reset_password", methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Register.query.filter_by(email = form.email.data).first()
        if user:
            user.reset_token_used = 0
            db.session.commit()

            send_reset_email(user)
            flash('An email has been sent with instructions to reset your password.', 'info')

            
            return redirect(url_for('customerLogin'))
        
    return render_template('customer/reset_request.html', Title = 'Reset Password', form=form)

@app.route("/customer/reset_password/<token>", methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = Register.verify_reset_token(token)

    if user is None or user.reset_token_used:
        flash('That is an invalid or expired token.','warning')
        return redirect(url_for('reset_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        user.reset_token_used = 1
        db.session.commit()

        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('customerLogin'))
    return render_template('customer/reset_token.html',title='Reset Password', form=form)