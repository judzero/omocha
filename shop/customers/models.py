from shop import db, app, login_manager
from datetime import datetime, timedelta
from flask_login import UserMixin
from sqlalchemy.ext.mutable import MutableDict
import json , jwt

@login_manager.user_loader
def user_loader(user_id):
    return Register.query.get(user_id)

class Register(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(50), unique= False)
    username = db.Column(db.String(50), unique= True)
    email = db.Column(db.String(50), unique= True)
    password = db.Column(db.String(200), unique= False)
    state = db.Column(db.String(50), unique= False)
    city = db.Column(db.String(50), unique= False)
    contact = db.Column(db.String(50), unique= False)
    address = db.Column(db.String(50), unique= False)
    zipcode = db.Column(db.String(50), unique= False)
    profile = db.Column(db.String(200), unique= False , default='profile.jpg')
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    reset_token_used = db.Column(db.Integer, default=0, nullable=False)


    
    def get_reset_token(self, expires_sec=1800):
        if not self.reset_token_used:
            reset_token = jwt.encode(
                {
                    "confirm": self.id,
                    "exp": datetime.now() + timedelta(seconds=expires_sec)
                },
                app.config['SECRET_KEY'],
                algorithm="HS256"
            )
            return reset_token
        else:
            return None
    
    
    @staticmethod
    def verify_reset_token(token):
        try:
            data = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                leeway=timedelta(seconds=10),
                algorithms=["HS256"]
            )
            user_id = data.get('confirm')
            user = Register.query.get(user_id)
            if user is None:
                return None  # Token is valid, but user not found
            # Update the confirmation status or perform additional checks if needed
            return user
        except jwt.ExpiredSignatureError:
            # Token has expired
            return None
        except jwt.InvalidTokenError:
            # Token is invalid
            return None
    def __repr__(self):
        return '<Register %r>' % self.name, self.password, self.email


class JsonEcodedDict(db.TypeDecorator):
    impl = db.Text
    def process_bind_param(self, value, dialect):
        if value is None:
            return '{}'
        else:
            return json.dumps(value)
    def process_result_value(self, value, dialect):
        if value is None:
            return {}
        else:
            return json.loads(value)

class CustomerOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)
    customer_id = db.Column(db.Integer, unique=False, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    stripe_product_id = db.Column(db.String(50))
    stripe_price_id = db.Column(db.String(50))
    orders = db.Column(MutableDict.as_mutable(db.JSON))

    def __repr__(self):
        return'<CustomerOrder %r>' % self.invoice


with app.app_context():
    db.create_all()




    


