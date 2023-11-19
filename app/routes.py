# app/routes.py
# pyright: reportMissingImports=false
import smtplib
import mailbox
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, render_template, flash, redirect, url_for, request
from app.forms import BookingForm
from app.models import Booking
from app import db
from paystackapi.paystack import Paystack
from app.service import submit_booking_to_database, is_date_available

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

            if booking_id and Booking:
                flash(f"Booking successful! Booking ID: {booking_id}", "success")

            # Redirect to payment gateway
                return redirect(url_for("booking.payment_gateway", booking_id=booking_id))

            else:
                flash("This date is not available. Please select another date.", "error")

    return render_template("book_now.html", form=form)



@booking_bp.route("/payment-gateway/<int:booking_id>")
def payment_gateway(booking_id):
    # Retrieve the booking details from the database based on the booking_id
    booking = Booking.query.get(booking_id)

    # Get the payment gateway information from the database
    payment_gateway = booking.payment_gateway

    if payment_gateway == "paystack":
        # Generate the Paystack payment URL
        paystack = Paystack(secret_key="your-paystack-secret-key")
        payment_url = paystack.initialize_transaction(
            amount=booking.total_amount,
            email=booking.email,
            reference=f"booking_{booking.id}"
        )

        # Redirect to the Paystack payment page
        return redirect(payment_url)

    else:
        flash("Invalid payment gateway", "error")
        return redirect(url_for("booking.home"))

def get_paystack_payment_url(booking_id):
    # Get Paystack payment URL for booking
    booking = Booking.query.get(booking_id)
    amount = booking.get_total_amount()
    email = booking.email
    reference = f"booking-{booking_id}"
    paystack_public_key = "pk_test_6909e7f4f51a6129594046a88564a029da555696"
    paystack_url = f"https://paystack.com/pay/your-paystack-key?amount={amount}&email={email}&reference={reference}"
    return paystack_url



def verify_paystack_signature(signature, payload):
    # Verify Paystack signature using your Paystack secret key
    paystack_secret_key = "sk_test_af92a730e440949266df258c540c717ba0cc72bb"
    paystack_api = Paystack(secret_key=paystack_secret_key)
    is_valid_signature = paystack_api.verify_signature(signature, payload)
    return is_valid_signature

def is_date_available(selected_date, selected_service_types):
    # Check date availability for each selected service type
    for service_type in selected_service_types:
        existing_bookings = Booking.query.filter_by(date=selected_date, service_type=service_type).all()

        if existing_bookings:
            return False

    return True

def send_confirmation_email(booking_id):
            # Retrieve booking details
            booking = Booking.query.get(booking_id)
            email = booking.email
            booking_date = booking.date.strftime("%B %d, %Y")
            service_type = booking.service_type
            total_amount = booking.get_total_amount()

            # Compose email message
            message = MIMEMultipart()
            message["From"] = "your-email@example.com"
            message["To"] = booking.email
            message["Subject"] = "Booking Confirmation"

            body = f"Dear Customer,\n\nThank you for booking with us. Your booking details are as follows:\n\nBooking ID: {booking_id}\nBooking Date: {booking_date}\nService Type: {service_type}\nTotal Amount: {total_amount}\n\nWe look forward to seeing you soon.\n\nBest regards,\nYour Booking Team"
            message.attach(MIMEText(body, "plain"))

            # Send email
            with smtplib.SMTP("your-smtp-server.com", 587) as server:
                server.starttls()
                server.login("your-email@example.com", "your-email-password")
                server.sendmail("your-email@example.com", booking.email, message.as_string())

            print("Confirmation email sent successfully!")

def submit_booking_to_database(form):
    # Create and commit booking record to the database
    booking = Booking(
        service_type=form.service_type.data,
        date=form.date.data,
        email=form.email.data,
        name=form.name.data,
        phone_number=form.phone_number.data,
        payment_gateway="paystack"
    )

    try:
        db.session.add(booking)
        db.session.commit()
        booking_id = booking.id

        flash(f"Booking successful! Booking ID: {booking_id}", "success")

        return booking_id
    except Exception as e:
        flash(f"Error creating booking: {e}", "error")
        return None
