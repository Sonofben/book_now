# app/routes.py
from mailbox import Mailbox
from flask import Blueprint, render_template, flash, redirect, url_for
from app.forms import BookingForm
from flask_mail import Mail, Message
from app.models import Booking, Service
from app import db
from app import logger

booking_bp = Blueprint("booking", __name__)

@booking_bp.route("/")
def home():
    # Query all bookings from the database
    bookings = Booking.query.all()
    return render_template("home.html", bookings=bookings)


@booking_bp.route("/book-now", methods=["GET", "POST"])
def book_now():
    form = BookingForm()

    if form.validate_on_submit():
        # Calculate total amount based on selected services and quantities
        total_amount = 0

        if form.category.data == "Sport":
            for service, _ in form.sport_services:
                quantity = getattr(form, f"{service.lower()}_quantity").data
                total_amount += quantity * form.prices.get(service, 0)
        elif form.category.data == "Leisure":
            quantity = getattr(form, "leisure_quantity").data
            total_amount += quantity * form.prices.get("Leisure", 0)

        # Check date availability for selected service types
        selected_service_types = form.service_type.data
        selected_date = form.date.data
        is_date_available = is_date_available(selected_date, selected_service_types)

        if is_date_available:
            # Submit booking to the database and get booking ID
            booking_id = submit_booking_to_database(form)
            flash(f"Booking successful! Booking ID: {booking_id}", "success")

            # Redirect to payment gateway
            return redirect(url_for("booking.payment_gateway", booking_id=booking_id))

        else:
            flash("This date is not available. Please select another date.", "error")

    return render_template("book_now.html", form=form)


@booking_bp.route("/payment-gateway/<int:booking_id>")
def payment_gateway(booking_id):
    booking = Booking.query.get(booking_id)
    payment_gateway = booking.payment_gateway

    if payment_gateway == "paystack":
        handle_paystack_payment(booking_id)
    elif payment_gateway == "stripe":
        # Implement Stripe payment handling logic here
        pass
    else:
        flash(f"Payment gateway not supported for this booking: {booking.payment_gateway}", "error")
        return redirect(url_for("booking.details", booking_id=booking_id))

def handle_paystack_payment(booking_id):
    # Implement Paystack payment processing logic here
    pass


def is_date_available(selected_date, selected_service_types):
    # Check date availability for each selected service type
    for service_type in selected_service_types:
        existing_bookings = Booking.query.filter_by(date=selected_date, service_type=service_type).all()

        if existing_bookings:
            return False

    return True

@booking_bp.route("/bookings/<int:booking_id>/cancel")
def cancel_booking(booking_id):
    booking = Booking.query.get(booking_id)
    refund_payment_paystack = None
    refund_payment_stripe = None
    if booking.is_cancellable():
        booking.cancel()
        db.session.commit()

        # Process refund if applicable
        if booking.payment_gateway == "paystack":
            refund_payment_paystack(booking_id)
        elif booking.payment_gateway == "stripe":
            refund_payment_stripe(booking_id)

        return redirect(url_for("booking.history"))
    else:
        flash("Booking cannot be canceled.", "error")
        return redirect(url_for("booking.details", booking_id=booking_id))


def send_confirmation_email(booking_id):
    booking = Booking.query.get(booking_id)
    message = Message('Booking Confirmation', sender='noreply@example.com', recipients=[booking.email])
    message.body = f"Dear {booking.name},\n\nYour booking has been confirmed. Booking ID: {booking_id}"
    Mailbox.send(message)


def submit_booking_to_database(form):
    # Create and commit booking record to the database
    booking = Booking(
        service_type=form.service_type.data,
        date=form.date.data,
        email=form.email.data,
        name=form.name.data,
        phone_number=form.phone_number.data
    )

    try:
        db.session.add(booking)
        db.session.commit()
        booking_id = booking.id

        # Send confirmation email after successful booking
        send_confirmation_email(booking_id)

        flash(f"Booking successful! Booking ID: {booking_id}", "success")

        # Redirect to payment gateway
        return redirect(url_for("booking.payment_gateway", booking_id=booking_id))
    except Exception as e:
        logger.error(str(e))
        flash(f"Error creating booking: {e}", "error")
        return None
