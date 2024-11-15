from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, SubmitField, StringField, DateTimeField
from wtforms.validators import DataRequired, NumberRange, Optional

class ServiceRequestForm(FlaskForm):
    service_date = DateTimeField('Preferred Date/Time', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    location = StringField('Service Location', validators=[DataRequired()])
    remarks = TextAreaField('Additional Notes', validators=[Optional()])
    submit = SubmitField('Submit Request')

class ReviewForm(FlaskForm):
    rating = IntegerField('Rating', validators=[DataRequired(), NumberRange(min=1, max=5)])
    review = TextAreaField('Review', validators=[DataRequired()])
    submit = SubmitField('Submit Review')
