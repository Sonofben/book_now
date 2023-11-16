# app/forms.py

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, DateField, BooleanField, SelectMultipleField, IntegerField
from wtforms.validators import DataRequired, Email, Optional
from wtforms.validators import EqualTo

class BookingForm(FlaskForm):
    sport_services = [
        ('Football', 'Football'),
        ('Basketball', 'Basketball'),
        ('Golf', 'Golf'),
        ('The Cage', 'The Cage')
    ]

    leisure_services = [
        ('Leisure', 'Leisure')
    ]

    service_types = {
        'Sport': sport_services,
        'Leisure': leisure_services
    }

    category = SelectField('Category', choices=[('Sport', 'Sport'), ('Leisure', 'Leisure')], validators=[DataRequired()])
    service_type = SelectMultipleField('Service Type', choices=[], validators=[Optional()])
    date = DateField('Date', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    agree_to_terms = BooleanField('Agree to Terms and Conditions', validators=[DataRequired()])
    confirm_email = StringField('Confirm Email', validators=[EqualTo('email', message="Emails must match")])
    total_amount = IntegerField('Total Amount', validators=[Optional()])

    # Placeholder: Update with actual prices for each service
    prices = {
        'Football': 34000,
        'Basketball': 25000,
        'Golf': 18000,
        'The Cage': 30000,
        'Leisure': 20000
    }

    def __init__(self, *args, **kwargs):
        super(BookingForm, self).__init__(*args, **kwargs)
        self.update_service_choices()

        for service, _ in self.sport_services:
            # Add a dynamic field for each sport service type to handle quantity
            setattr(self, f'{service.lower()}_quantity', IntegerField(f'{service} Quantity', default=0))

        # Add a dynamic field for Leisure service type to handle quantity
        setattr(self, 'leisure_quantity', IntegerField('Leisure Quantity', default=0))

    def update_service_choices(self):
        # Update service_type choices based on the selected category
        selected_category = self.category.data
        choices = self.service_types.get(selected_category, [])
        self.service_type.choices = choices

    def validate(self):
        if not super(BookingForm, self).validate():
            return False

        # Calculate the total amount based on the selected services and their quantities
        total_amount = 0
        for service, _ in self.service_type.choices:
            quantity = getattr(self, f'{service.lower()}_quantity').data
            total_amount += quantity * self.prices.get(service, 0)

        # Update the total_amount field with the calculated value
        self.total_amount.data = total_amount

        return True
