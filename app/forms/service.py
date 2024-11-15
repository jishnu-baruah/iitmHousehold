from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ServiceForm(FlaskForm):
    name = StringField("Service Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    base_price = FloatField("Base Price", validators=[DataRequired(), NumberRange(min=0)])
    time_required = IntegerField("Time Required (minutes)", validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField("Submit")
