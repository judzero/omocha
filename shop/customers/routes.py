from flask import render_template, session, request, redirect,url_for,flash,current_app,jsonify
from shop import app,db,photos,bcrypt,login_manager, mail
from flask_login import login_required, current_user, login_user, logout_user
from .forms import CustomerRegisterForm , CustomerLoginForm, RequestResetForm, ResetPasswordForm
from .models import Register, CustomerOrder
import secrets
import os
from flask_mail import Message
import traceback


import stripe

app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51OOkWEK4Yt7azovvDWXIAPJOzZOwq533hXqqZUQGwzQdHZioL4jQrQXTzI8cdeUNyaG1YVVRQuyZ52QFmEhLJksu00EN8c75Kq'
stripe.api_key='sk_test_51OOkWEK4Yt7azovvCahoEAIVsyZ8o2eSoBzPc3mWgyy2TRpbV36lHzGFue42JxY9yOXzEoKXFD2pae9eES1N1VMt00S4myQB3y'

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

        try:
            data = request.get_json(force=True)
            print("Received Data:", data)
            product_name = data.get('productName', 'Default Product Name')
            price = data.get('price', 0)
            quantity = data.get('quantity', 0)
            
            print(product_name)
            print(price)
            print(quantity)
            for product_name in data.items():
                product_name = data.get('productName', 'Default Product Name')
                price = data.get('price', 0)
                quantity = data.get('quantity', 0)


            # Assuming session['ShoppingCart'] contains the details of the order
                order = CustomerOrder(invoice=invoice, customer_id=customer_id, orders=session['ShoppingCart'])
                db.session.add(order)
                db.session.commit()

                print("Product Name:", product_name)
                print("p:", price)
                print("q:", quantity)

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

            # Retrieve the Stripe product ID and associate it with the order
                order.stripe_product_id = stripe_product.id
                order.stripe_price_id = stripe_price.id
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
        

@app.route('/stripe_pay', methods=["POST"])
def stripe_pay():
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        data = request.get_json(force=True)
        quantity = data.get('quantity', 0)
        order = CustomerOrder(invoice=invoice, customer_id=customer_id)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': order.stripe_price_id,
                'quantity': quantity,
            }],
            mode='payment',
            success_url=url_for('home', _external=True) + f'?session_id={session["customer_id"]}',
            cancel_url=url_for('index', _external=True),
        )
        return {
            'checkout_session_id': session['customer_id'], 
            'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
        }

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