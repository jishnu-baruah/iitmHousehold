from app import db
from datetime import datetime
import json

class Payment(db.Model):
    __tablename__ = "payment"
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("service_request.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey("professional.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending/completed/failed/refunded
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    invoice_number = db.Column(db.String(50), unique=True)
    payment_details = db.Column(db.Text)  # JSON string for additional details
    
    def __init__(self, **kwargs):
        super(Payment, self).__init__(**kwargs)
        self.generate_invoice_number()

    def generate_invoice_number(self):
        """Generate unique invoice number"""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        self.invoice_number = f"INV-{timestamp}-{self.customer_id}"

    def process_payment(self, payment_details):
        try:
            # Simulate payment processing
            self.payment_details = json.dumps(payment_details)
            self.status = "completed"
            self.completed_at = datetime.utcnow()
            self.transaction_id = f"TXN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            # Update professional earnings
            from app.models.user import Professional
            professional = Professional.query.get(self.professional_id)
            if professional:
                professional.update_earnings(self.amount)
            
            # Update customer spent amount
            from app.models.user import Customer
            customer = Customer.query.get(self.customer_id)
            if customer:
                customer.update_total_spent(self.amount)
            
            db.session.commit()
            return True, "Payment processed successfully"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def generate_invoice(self):
        """Generate invoice data"""
        from app.models.user import Customer, Professional
        from app.models.request import ServiceRequest
        
        customer = Customer.query.get(self.customer_id)
        professional = Professional.query.get(self.professional_id)
        service_request = ServiceRequest.query.get(self.request_id)
        
        return {
            "invoice_number": self.invoice_number,
            "date": self.created_at.strftime("%Y-%m-%d"),
            "customer": {
                "name": customer.username,
                "address": customer.address,
                "phone": customer.phone
            },
            "professional": {
                "name": professional.username,
                "service_type": professional.service_type
            },
            "service": {
                "name": service_request.service.name,
                "description": service_request.service.description
            },
            "amount": self.amount,
            "status": self.status,
            "payment_method": self.payment_method,
            "transaction_id": self.transaction_id
        }

    def to_dict(self):
        return {
            "id": self.id,
            "invoice_number": self.invoice_number,
            "amount": self.amount,
            "status": self.status,
            "payment_method": self.payment_method,
            "transaction_id": self.transaction_id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "completed_at": self.completed_at.strftime("%Y-%m-%d %H:%M:%S") if self.completed_at else None
        }

class Invoice(db.Model):
    __tablename__ = "invoice"
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey("payment.id"), nullable=False)
    invoice_number = db.Column(db.String(50), unique=True)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    subtotal = db.Column(db.Float)
    tax = db.Column(db.Float)
    total = db.Column(db.Float)
    notes = db.Column(db.Text)
    is_paid = db.Column(db.Boolean, default=False)
