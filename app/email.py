# app/email.py
from flask_mail import Message
from app import mail

def send_booking_email(booking):
    msg = Message('Booking Confirmation', recipients=[booking.email])
    msg.body = f"Hi {booking.name},\n\nThank you for booking with us. Your booking details are as follows:\n\nDate: {booking.date}\nServices: {', '.join(booking.services)}\nTotal Amount: {booking.total_amount}\n\nWe look forward to seeing you soon!\n\nBest regards,\nThe Booking Team"
    mail.send(msg)