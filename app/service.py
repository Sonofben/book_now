# app/service.py
from app.models import Booking
from app import db
from app.routes import send_confirmation_email


def submit_booking_to_database(form):
    booking = create_booking_from_form(form)
    save_booking(booking)
    send_confirmation_email(booking.id)
    return booking.id, booking

def create_booking_from_form(form):
    return Booking(
        service_type=form.service_type.data,
        date=form.date.data,
        email=form.email.data,
        name=form.name.data,
        phone_number=form.phone_number.data,
        payment_gateway="paystack"
    )

def save_booking(booking):
    db.session.add(booking)
    db.session.commit()

def is_date_available(selected_date, selected_service_types):
    for service_type in selected_service_types:
        existing_bookings = Booking.query.filter_by(date=selected_date, service_type=service_type).all()
        if existing_bookings:
            return False
    return True
