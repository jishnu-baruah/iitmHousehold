from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, DecimalField
from wtforms.validators import DataRequired, Length

class PaymentForm(FlaskForm):
    payment_method = SelectField('Payment Method', 
        choices=[
            ('credit_card', 'Credit Card'),
            ('debit_card', 'Debit Card'),
            ('upi', 'UPI'),
            ('net_banking', 'Net Banking')
        ],
        validators=[DataRequired()]
    )
    card_number = StringField('Card Number', validators=[Length(min=16, max=16)])
    card_holder = StringField('Card Holder Name', validators=[DataRequired()])
    expiry_month = SelectField('Expiry Month', 
        choices=[(str(i), str(i)) for i in range(1, 13)],
        validators=[DataRequired()]
    )
    expiry_year = SelectField('Expiry Year',
        choices=[(str(i), str(i)) for i in range(2024, 2035)],
        validators=[DataRequired()]
    )
    cvv = StringField('CVV', validators=[Length(min=3, max=3)])
    submit = SubmitField('Process Payment')

class UPIPaymentForm(FlaskForm):
    upi_id = StringField('UPI ID', validators=[DataRequired()])
    submit = SubmitField('Pay Now')

class RefundForm(FlaskForm):
    reason = StringField('Reason for Refund', validators=[DataRequired()])
    amount = DecimalField('Refund Amount', validators=[DataRequired()])
    submit = SubmitField('Process Refund')
