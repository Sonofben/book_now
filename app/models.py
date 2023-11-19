# app/models.py

from app import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask import current_app
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float(precision=10, scale=2), nullable=False)

class Booking(db.Model):
    """
    Represents a booking made by a user.

    Attributes:
        id (int): The unique identifier for the booking.
        service_type (str): The type of service being booked.
        date (datetime.date): The date of the booking.
        email (str): The email address of the user making the booking.
        name (str): The name of the user making the booking.
        phone_number (str): The phone number of the user making the booking.
        service_id (int): The foreign key referencing the associated service.
        service (Service): The associated service for the booking.

    Methods:
        save(): Saves the booking to the database.
    """

    id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)

    # Establish a relationship between Booking and Service models
    service_id = db.Column(db.Integer, ForeignKey('service.id'))
    service = relationship("Service", backref="bookings")
    

    def save(self):
        """
        Saves the booking to the database.

        This method adds the current booking instance to the database session and commits the changes.
        """
        db = current_app.db
        db.session.add(self)
        db.session.commit()