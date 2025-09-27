from flask_sqlalchemy import SQLAlchemy



db = SQLAlchemy()

# ---------------- Models ---------------- #

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    ph_num = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    reservations = db.relationship('Reservation', backref='user', lazy=True)


class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    ph_num = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Lot(db.Model):
    __tablename__ = 'lot'
    id = db.Column(db.Integer, primary_key=True)
    loc = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    max_spots = db.Column(db.Integer, nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    spots = db.relationship('Spot', backref='lot', lazy=True)
    reservations = db.relationship('Reservation', backref='lot', lazy=True)


class Spot(db.Model):
    __tablename__ = 'spot'
    id = db.Column(db.Integer, primary_key=True)
    spot_number = db.Column(db.Integer)
    l_id = db.Column(db.Integer, db.ForeignKey('lot.id'), nullable=False)
    status = db.Column(db.String(1), default='A')  
    reg_num = db.Column(db.String(20), nullable=True)
    reservations = db.relationship('Reservation', backref='spot', lazy=True)


class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    u_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    l_id = db.Column(db.Integer, db.ForeignKey('lot.id'), nullable=True)
    s_id = db.Column(db.Integer, db.ForeignKey('spot.id'), nullable=True)
    reg_num = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    cost = db.Column(db.Float)

