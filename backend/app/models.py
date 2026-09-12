from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from .extensions import db

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    # Relationships
    equipment = db.relationship('Equipment', backref='owner', lazy='dynamic', foreign_keys='Equipment.owner_id')
    rental_requests_made = db.relationship('RentalRequest', backref='renter', lazy='dynamic', foreign_keys='RentalRequest.renter_id')
    rentals_as_renter = db.relationship('Rental', backref='renter_user', lazy='dynamic', foreign_keys='Rental.renter_id')
    rentals_as_owner = db.relationship('Rental', backref='owner_user', lazy='dynamic', foreign_keys='Rental.owner_id')
    reviews = db.relationship('Review', backref='reviewer', lazy='dynamic')

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    equipment = db.relationship('Equipment', backref='category', lazy='dynamic')

class Equipment(db.Model):
    __tablename__ = 'equipment'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    condition = db.Column(db.String(50))
    price_per_day = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(200))
    availability_status = db.Column(db.String(20), default='available')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    rental_requests = db.relationship('RentalRequest', backref='equipment', lazy='dynamic')
    rentals = db.relationship('Rental', backref='equipment_item', lazy='dynamic')

class RentalRequest(db.Model):
    __tablename__ = 'rental_request'
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    renter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='PENDING')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    rental = db.relationship('Rental', backref='request', uselist=False)

class Rental(db.Model):
    __tablename__ = 'rental'
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('rental_request.id'), nullable=False, unique=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    renter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='ACTIVE')
    returned_at = db.Column(db.DateTime)

    reviews = db.relationship('Review', backref='rental', lazy='dynamic')

class Review(db.Model):
    __tablename__ = 'review'
    id = db.Column(db.Integer, primary_key=True)
    rental_id = db.Column(db.Integer, db.ForeignKey('rental.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = 'notification'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Report(db.Model):
    __tablename__ = 'report'
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='OPEN')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
