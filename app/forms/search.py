from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, DecimalField
from wtforms.validators import Optional

class SearchForm(FlaskForm):
    query = StringField('Service Name')
    location = StringField('Location')
    pincode = StringField('PIN Code')
    service_type = SelectField('Service Type', choices=[
        ('', 'All Services'),
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('cleaning', 'Cleaning'),
        ('carpentry', 'Carpentry'),
        ('painting', 'Painting'),
        ('appliance', 'Appliance Repair'),
        ('pest_control', 'Pest Control'),
        ('gardening', 'Gardening')
    ], validators=[Optional()])
    price_range = SelectField('Price Range', choices=[
        ('', 'Any Price'),
        ('0-50', 'Under $50'),
        ('50-100', '$50 - $100'),
        ('100-200', '$100 - $200'),
        ('200+', 'Over $200')
    ], validators=[Optional()])
    submit = SubmitField('Search')
