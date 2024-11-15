from app import db
from datetime import datetime

class ServiceRequest(db.Model):
    __tablename__ = "service_request"
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey("professional.id"))
    date_of_request = db.Column(db.DateTime, default=datetime.utcnow)
    date_of_completion = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="requested")
    remarks = db.Column(db.Text)
    rating = db.Column(db.Integer)
    review = db.Column(db.Text)

    # Relationships
    service = db.relationship("Service", back_populates="service_requests")
    professional = db.relationship("Professional", back_populates="service_requests")
    customer = db.relationship("Customer", back_populates="service_requests")
