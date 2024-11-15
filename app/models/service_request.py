from app import db

class ServiceRequest(db.Model):
    __tablename__ = 'service_request'

    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)  # Ensure this is included
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)

    # Relationships
    professional = db.relationship('Professional', back_populates='service_requests')
    customer = db.relationship('Customer', back_populates='service_requests')  # Add this line
    service = db.relationship('Service', back_populates='service_requests')

    def __repr__(self):
        return f'<ServiceRequest {self.id}>'
