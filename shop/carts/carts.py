from flask import render_template,session, request,redirect,url_for,flash,current_app
from shop import db , app
from shop.products.models import Addproduct
from shop.products.routes import brands, categories
import json


def MagerDicts(dict1,dict2):
    if isinstance(dict1, list) and isinstance(dict2,list):
        return dict1  + dict2
    if isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))

@app.route('/addcart', methods=['POST'])
def AddCart():
    try:
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity'))

        if product_id and quantity and request.method == 'POST':
            product = Addproduct.query.filter_by(id=product_id).first()

            if product and product.stock >= quantity:
                item = {
                    'name': product.name,
                    'price': product.price,
                    'discount': product.discount,
                    'quantity': quantity,
                    'image': product.image_1
                }

                session.setdefault('ShoppingCart', {})
                shopping_cart = session['ShoppingCart']

                if product_id in shopping_cart:
                    shopping_cart[product_id]['quantity'] += quantity
                else:
                    shopping_cart[product_id] = item

                # Update the stock in the database
                product.stock -= quantity
                db.session.commit()

                session.modified = True

    except Exception as e:
        print(e)

    finally:
        return redirect(request.referrer)
    
# JALIFOGO TEST
@app.route('/cart')
def getCart():
    if 'ShoppingCart' not in session:
        return redirect(request.referrer)
    return render_template('products/cart.html', brands = brands(), categories = categories())

@app.route('/deleteitem/<int:id>')
def deleteitem(id):
    if 'ShoppingCart' not in session and len(session['ShoppingCart']) <= 0:
        return redirect(url_for('home'))
    try:
        session.modified = True
        for key, item in session['ShoppingCart'].items():
            if int(key) == id:
                session['ShoppingCart'].pop(key,None)
                return redirect(url_for('getCart'))
    except Exception as e:
        print(e)
        return redirect(url_for('getCart'))
    

@app.route('/clearcart')
def clearcart():
    try:
        shopping_cart = session.get('ShoppingCart', {})
        
        # Iterate through items in the shopping cart
        for product_id, item in shopping_cart.items():
            quantity_in_cart = item.get('quantity', 0)

            # Retrieve the product from the database
            product = Addproduct.query.filter_by(id=product_id).first()

            if product:
                # Return the stock to the database
                product.stock += quantity_in_cart

        # Clear the shopping cart in the session
        session.pop('ShoppingCart', None)
        
        db.session.commit()  # Commit changes to the database

    except Exception as e:
        print(f"An error occurred: {e}")

    return redirect(url_for('home'))