from wtforms import Form, SubmitField,IntegerField,FloatField,StringField,TextAreaField,validators,DecimalField
from flask_wtf.file import FileField,FileRequired,FileAllowed

class Addproducts(Form):
    product_code = StringField('Product Code :', [validators.DataRequired()])
    name = StringField('Product Name :', [validators.DataRequired()])
    price = DecimalField('Price :', [validators.DataRequired()])
    discount = IntegerField('Discount :', default=0)
    stock = IntegerField('Stocks :', [validators.DataRequired()])
    description = TextAreaField('Description :', [validators.DataRequired()])

    image_1 = FileField('Upload Image', validators=[FileAllowed(['jpg, jpeg, png'],'images only!')])

