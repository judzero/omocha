from shop import db,app
from datetime import datetime


class Addproduct(db.Model):
    __seachabale__ = ['name','desc']
    id = db.Column(db.Integer, primary_key=True)
    product_code = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Numeric(10,2), nullable=False)
    discount = db.Column(db.Integer, default=0)
    stock = db.Column(db.Integer, nullable=False)
    desc = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False,default=datetime.today)

    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'),nullable=False)
    brand = db.relationship('Brand',backref=db.backref('brands', lazy=True))

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'),nullable=False)
    category = db.relationship('Category',backref=db.backref('categories', lazy=True))
    

    image_1 = db.Column(db.String(150), nullable=False, default='image1.jpg')

    def __repr__(self):
        return '<Post %r>' % self.name
    
    def __repr__(self):
        return '<Post:{}>'.format(self.title)

class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    def __repr__(self):
        return '<Brand %r>' % self.name
    
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    def __repr__(self):
        return '<Catgory %r>' % self.name
    
with app.app_context():
    db.create_all()