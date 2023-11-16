# app/models.py

from app import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float(10, 2), nullable=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)

    # Establish a relationship between Booking and Service models
    service_id = db.Column(db.Integer, ForeignKey('service_id'))
    service = relationship("Service", backref="bookings")
