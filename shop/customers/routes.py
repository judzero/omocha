from flask import render_template, session, request, redirect,url_for,flash,current_app
from shop import app,db,photos,bcrypt,login_manager
from flask_login import login_required, current_user, login_user, logout_user
from .forms import CustomerRegisterForm , CustomerLoginForm
from .models import Register
import secrets
import os


@app.route('/customer/register', methods=['GET','POST'])
def customer_register():
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        register = Register(name=form.name.data, username=form.username.data, email=form.email.data,password=hash_password,city=form.city.data,contact=form.contact.data, address=form.address.data, zipcode=form.zipcode.data)
        db.session.add(register)
        flash(f'Register Successful!', 'success')
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('customer/register.html', form=form)

@app.route('/customer/login', methods=['GET', 'POST'])
def customerLogin():
    form = CustomerLoginForm()
    if form.validate_on_submit():
        user = Register.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Welcome! {form.name.data}', 'success')
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        flash('Incorrect Email or Password')
        return redirect(url_for('customerLogin'))
    return render_template('customer/login.html', form = form)