from flask import Flask, render_template, url_for, request, redirect, session, flash
from shop import app,db,bcrypt
from flask_sqlalchemy import SQLAlchemy
from .forms import RegistrationForm, LoginForm
from .models import User
from shop.products.models import Addproduct,Brand,Category
import os


@app.route('/brands')
def brands():
    if 'email' not in session:
        flash(f'Please Log In before accessing this page', 'danger')
        return redirect(url_for('login'))
    brands = Brand.query.order_by(Brand.id.desc()).all()
    return render_template('admin/brand.html', brands=brands)
    
@app.route('/category')
def category():
    if 'email' not in session:
        flash(f'Please Log In before accessing this page', 'danger')
        return redirect(url_for('login'))
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template('admin/brand.html', categories=categories)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        user = User(name = form.name.data,username = form.username.data, email = form.email.data,
                    password = hash_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('admin/register.html', form=form, title = "Registration Page")



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['email'] = form.email.data
            flash(f'Log In Successful!, Welcome! {form.email.data}', 'success')
            return redirect(url_for('seller'))
        else:
            flash('Invalid email or password. Please double-check your email and password and try again.', 'danger')
    return render_template('admin/login.html', form=form, title="Log In Page")


@app.route('/seller')
def dashboard():
    if 'email' not in session:
        flash(f'Please Log In before accessing this page', 'danger')
        return redirect(url_for('login'))
    products = Addproduct.query.all()
    return render_template('admin/dashboard.html', products=products)

