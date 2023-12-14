from flask import render_template,session, request,redirect,url_for,flash,current_app
from sqlalchemy import or_
from shop import db,photos,app,IMAGES,search
from .models import Category,Brand,Addproduct
from .forms import Addproducts
import secrets
import os


def brands():
    brands = Brand.query.join(Addproduct, (Brand.id == Addproduct.brand_id)).all()
    return brands

def categories():
    categories = Category.query.join(Addproduct,(Category.id == Addproduct.category_id)).all()
    return categories

@app.route('/')
def home():
    products = Addproduct.query.filter(Addproduct.stock > 0)
    return render_template('products/index.html', products=products,brands=brands(),categories=categories())

@app.route('/about')
def about():
    if 'email' not in session:
        flash(f'Please Log In before accessing this page', 'danger')
        return redirect(url_for('login'))
    return render_template('products/about.html')

@app.route('/new')
def new():
    return 'SOMEDAY MAGKAKAROON DIN TO NG NEW ITEMS'

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/result')
def result():
    searchword = request.form.get('q')
    products = Addproduct.query.msearch(searchword, fields=['name']).all()
    return render_template('products/result.html',products=products)


# @app.route('/search', methods=['GET', 'POST'])
# def search():
#     if request.method == 'POST':
#         search_query = request.form.get('search_query')
#         if search_query:
#             # Perform a simple text search on the 'name' and 'desc' fields
#             results = (
#                 Addproduct.query
#                 .filter(
#                     or_(
#                         Addproduct.name.ilike(f"%{search_query}%"),
#                         Addproduct.desc.ilike(f"%{search_query}%")
#                     )
#                 )
#                 .all()
#             )
#             return render_template('products/index.html', results=results, search_query=search_query)
#     return render_template('products/result.html')

@app.route('/brand/<int:id>')
def get_brand(id):
    page = request.args.get('page', 1, type=int)
    get_br = Brand.query.filter_by(id=id).first_or_404()
    brand = Addproduct.query.filter_by(brand=get_br).order_by(Addproduct.id.desc()).paginate(page=page, per_page=4)
    return render_template('products/index.html',brand=brand,brands=brands(),categories=categories(),get_br=get_br)

@app.route('/product/<int:id>')
def product_info(id):
    product = Addproduct.query.get_or_404(id)
    return render_template('products/product.html',product=product,brands=brands(),categories=categories())

@app.route('/categories/<int:id>')
def get_category(id):
    page = request.args.get('page', 1, type=int)
    get_cat = Category.query.filter_by(id=id).first_or_404()
    get_cat_prod = Addproduct.query.filter_by(category = get_cat).order_by(Addproduct.id.desc()).paginate(page=page, per_page=4)
    return render_template('products/index.html', get_cat_prod=get_cat_prod ,categories=categories(),brands=brands(),get_cat=get_cat)

@app.route('/addbrand',methods=['GET','POST'])
def addbrand():
    if 'email' not in session:
        flash(f'Please Log In first!', 'danger')
        return redirect(url_for('login')) 
    if request.method =="POST":
        getbrand = request.form.get('brand')
        brand = Brand(name=getbrand)
        db.session.add(brand)
        flash(f'The brand "{getbrand}" was added to your database','success')
        db.session.commit()
        return redirect(url_for('addbrand'))
    return render_template('products/addbrand.html', title='Add brand',brands='brands')

@app.route('/updatebrand/<int:id>',methods=['GET','POST'])
def updatebrand(id):
    if 'email' not in session:
        flash('Login first please','danger')
        return redirect(url_for('login'))
    updatebrand = Brand.query.get_or_404(id)
    brand = request.form.get('brand')
    if request.method =="POST":
        updatebrand.name = brand
        flash(f'The brand {updatebrand.name} was changed to {brand}','success')
        db.session.commit()
        return redirect(url_for('brands'))
    brand = updatebrand.name
    return render_template('products/updatebrand.html', title='Update brand',brands='brands',updatebrand=updatebrand)


# @app.route('/deletebrand/<int:id>', methods=['POST'])
# def deletebrand(id):
#     brand = Brand.query.get_or_404(id)
#     if request.method=="POST":
#         db.session.delete(brand)
#         flash(f"The brand {brand.name} was deleted from your database","success")
#         db.session.commit()
#         return redirect(url_for('seller'))
#     flash(f"The brand {brand.name} can't be  deleted from your database","warning")
#     return redirect(url_for('seller'))

@app.route('/addcategory',methods=['GET','POST'])
def addcategory():
    if 'email' not in session:
        flash(f'Please Log In first!', 'danger')
        return redirect(url_for('login'))
    if request.method =="POST":
        getcategory = request.form.get('category')
        category = Category(name=getcategory)
        db.session.add(category)
        flash(f'The brand "{getcategory}" was added to your database','success')
        db.session.commit()
        return redirect(url_for('addcategory'))
    return render_template('products/addbrand.html', title='Add category')

@app.route('/updatecategory/<int:id>',methods=['GET','POST'])
def updatecategory(id):
    if 'email' not in session:
        flash('Login first please','danger')
        return redirect(url_for('login'))
    updatecategory = Category.query.get_or_404(id)
    category = request.form.get('category')  
    if request.method =="POST":
        updatecategory.name = category
        flash(f'The category {updatecategory.name} was changed to {category}','success')
        db.session.commit()
        return redirect(url_for('category'))
    category = updatecategory.name
    return render_template('products/updatebrand.html', title='Update cat', updatecategory=updatecategory)

# # @app.route('/deletecategory/<int:id>', methods=['GET','POST'])
# # def deletecategory(id):
#     category = Category.query.get_or_404(id)
#     if request.method=="POST":
#         db.session.delete(category)
#         flash(f"The brand {category.name} was deleted from your database","success")
#         db.session.commit()
#         return redirect(url_for('seller'))
#     flash(f"The brand {category.name} can't be  deleted from your database","warning")
#     return redirect(url_for('seller'))

@app.route('/addproduct', methods=['GET','POST'])
def addproduct():
    if 'email' not in session:
        flash(f'Please Log In first!', 'danger')
        return redirect(url_for('login'))
    form = Addproducts(request.form)
    brands = Brand.query.all()
    categories = Category.query.all()
    if 'email' not in session:
        flash(f'Please Log In first!', 'danger')
        return redirect(url_for('login'))
    if request.method=="POST" and 'image_1' in request.files:
        product_code = form.product_code.data
        name = form.name.data
        price = form.price.data
        discount = form.discount.data
        categories = int(request.form.get('category'))
        brands = int(request.form.get('brand'))
        stock = form.stock.data
        desc = form.description.data
        image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        addproduct = Addproduct(product_code = product_code,name=name,price=price,discount=discount,category_id=categories,brand_id=brands,stock=stock,desc=desc,image_1=image_1)
        db.session.add(addproduct)
        flash(f'The product "{name}" was added in database','success')
        db.session.commit()
        return redirect(url_for('seller'))
    # images = db.session.query(Addproduct).all()
    # image_list = [img.image_1 for img in images]
    return render_template('products/addproduct.html', form=form, title='Add a Product', brands=brands,categories=categories)#, image_list=image_list)

@app.route('/updateproduct/<int:id>', methods=['GET','POST'])
def updateproduct(id):
    form = Addproducts(request.form)
    product = Addproduct.query.get_or_404(id)
    brands = Brand.query.all()
    categories = Category.query.all()
    brand = request.form.get('brand')
    category = request.form.get('category')
    if request.method =="POST":
        product.product_code = form.product_code.data
        product.name = form.name.data 
        product.price = form.price.data
        product.discount = form.discount.data
        product.stock = form.stock.data 
        product.desc = form.description.data
        product.category_id = category
        product.brand_id = brand
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            except:
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        flash('The product was updated','success')
        db.session.commit()
        return redirect(url_for('seller'))
    form.product_code.data = product.product_code
    form.name.data = product.name
    form.price.data = product.price
    form.discount.data = product.discount
    form.stock.data = product.stock
    form.description.data = product.desc
    brand = product.brand.name
    category = product.category.name
    return render_template('products/updateproduct.html', form=form, title='Update Product',product=product, brands=brands,categories=categories)

# # @app.route('/deleteproduct/<int:id>', methods=['POST'])
# # def deleteproduct(id):
#     product = Addproduct.query.get_or_404(id)
#     if request.method =="POST":
#         try:
#             os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
#         except Exception as e:
#             print(e)
#         db.session.delete(product)
#         db.session.commit()
#         flash(f'The product {product.name} was delete from your record','success')
#         return redirect(url_for('seller'))
#     flash(f'Can not delete the product','success')
#     return redirect(url_for('seller'))