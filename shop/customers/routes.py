from sqlalchemy import desc
from sqlalchemy.ext.mutable import MutableDict
from flask import render_template, session, request, redirect,url_for,flash,current_app,jsonify
from shop import app,db,photos,bcrypt,login_manager, mail
from flask_login import login_required, current_user, login_user, logout_user
from .forms import CustomerRegisterForm , CustomerLoginForm, RequestResetForm, ResetPasswordForm
from .models import Register, CustomerOrder
import secrets
import os
from flask_mail import Message
import traceback

import json
import stripe

app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51OOkWEK4Yt7azovvDWXIAPJOzZOwq533hXqqZUQGwzQdHZioL4jQrQXTzI8cdeUNyaG1YVVRQuyZ52QFmEhLJksu00EN8c75Kq'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51OOkWEK4Yt7azovvCahoEAIVsyZ8o2eSoBzPc3mWgyy2TRpbV36lHzGFue42JxY9yOXzEoKXFD2pae9eES1N1VMt00S4myQB3y'
stripe.api_key= app.config['STRIPE_SECRET_KEY']
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

@app.route('/customer/order', methods=['POST'])
def get_order():
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        order = CustomerOrder(invoice=invoice, customer_id=customer_id, orders=session['ShoppingCart'])
    
        try:
            order_data = request.json.get('products')

            for product in order_data:
                product_name = product.get('productName', 'N/A')
                price = product.get('ProdInfo', {}).get('price', 0)
                quantity = product.get('ProdInfo', {}).get('quantity', 0)

                # Create a product in Stripe
                product_type = "good"  # Replace with your actual product type ('service' or 'good')
                stripe_product = stripe.Product.create(name=product_name, type=product_type)

                # Create a price for the product
                price_amount = price
                price_currency = "usd"  # Replace with the actual currency
                stripe_price = stripe.Price.create(
                    product=stripe_product.id,
                    unit_amount=price_amount,
                    currency=price_currency,
                )

                # Update stripe_price_id dictionary
                if order.stripe_price_id is None:
                    order.stripe_price_id = {}
                
                order.stripe_price_id[stripe_product.id] = {
                    'price_id': stripe_price.id,
                    'quantity': quantity
                }

            print(order.stripe_price_id)
            db.session.add(order)
            db.session.commit()


            flash('Your order has been sent!', 'success')
            return jsonify(message='Order processed successfully')

        except stripe.error.StripeError as e:
            return jsonify(error=str(e)), 500
        except Exception as e:
            traceback.print_exc()
        return jsonify(error='Error getting your order')
    else:
        return redirect(url_for('customerLogin'))
        

@app.route('/create-checkout-session', methods=["POST"])
def create_checkout_session():
    if current_user.is_authenticated:
        stripe_price_ids = CustomerOrder.query \
    .with_entities(CustomerOrder.stripe_price_id) \
    .filter(CustomerOrder.stripe_price_id.isnot(None)) \
    .order_by(desc(CustomerOrder.id)) \
    .limit(1) \
    .all()
        if stripe_price_ids:
                stripe_price_values = stripe_price_ids[0][0]
                print("you were e")
                line_items = []
                for outer_key, inner_dict in stripe_price_values.items():
         
                        quantity = inner_dict.get('quantity', 0)
                        price_id = inner_dict.get('price_id','N/A')

                        line_item = {'price': price_id,
                                      'quantity': quantity }

                        line_items.append(line_item)
                        print(line_items)
                        session = stripe.checkout.Session.create(
                                line_items=line_items,
                                mode='payment',
                                success_url=url_for('home', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
                                cancel_url=url_for('getCart', _external=True),
                                )
    print(f"Checkout Session ID: {session['id']}")
    print(f"Public Key: {app.config['STRIPE_PUBLIC_KEY']}")

    return {'checkout_session_id': session['id'], 
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']}



    

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

# JALIFOGO TEST      
@app.route('/orders/<invoice>')
@login_required
def orders(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        customer = Register.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
        for _key, product in orders.orders.items():
            discount = (product['discount']/100) * float(product['price'])
            subTotal += float(product['price']) * int(product['quantity'])
            subTotal -= discount
            tax = ("%.2f" % (.06 * float(subTotal)))
            grandTotal = ("%.2f" % (1.06 * float(subTotal)))

    else:
        return redirect(url_for('customerLogin'))
    return render_template('customer/order.html', invoice=invoice, tax=tax,subTotal=subTotal,grandTotal=grandTotal,customer=customer,orders=orders)

@app.route('/payment',methods=['POST'])
def payment():
    invoice = request.get('invoice')
    amount = request.form.get('amount')
    customer = stripe.Customer.create(
      email=request.form['stripeEmail'],
      source=request.form['stripeToken'],
    )
    charge = stripe.Charge.create(
      customer=customer.id,
      description='Myshop',
      amount=amount,
      currency='usd',
    )
    orders =  CustomerOrder.query.filter_by(customer_id = current_user.id,invoice=invoice).order_by(CustomerOrder.id.desc()).first()
    orders.status = 'Paid'
    db.session.commit()
    return redirect(url_for('thank_you'))