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
        product = Addproduct.query.filter_by(id=product_id).first()
        if product_id and quantity and request.method == 'POST':
            DictItems = {
                product_id:{
                    'name' : product.name,
                    'price':product.price,
                    'discount':product.discount,
                    'quantity':quantity,
                    'image':product.image_1}}
            if 'ShoppingCart' in session:
                print(session['ShoppingCart'])
                if product_id in session['ShoppingCart']:
                    for key, item in session['ShoppingCart'].items():
                        if int(key) == int(product_id):
                            session.modified = True
                            item['quantity'] += 1
                else:
                    session['ShoppingCart'] = MagerDicts(session['ShoppingCart'], DictItems)    
            else:
                session['ShoppingCart'] = DictItems
                return redirect(request.referrer)
    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)
    
    
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
        session.pop('ShoppingCart', None)
        return redirect(url_for('home'))
    except Exception as e:
        print(e)
    
