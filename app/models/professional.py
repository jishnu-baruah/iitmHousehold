from app import db

class Professional(db.Model):
    __tablename__ = 'professional'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    expertise = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    __table_args__ = {'extend_existing': True}  # Allow redefining the existing table

    # Use a string reference for the relationship to avoid circular dependency issues
    service_requests = db.relationship('ServiceRequest', back_populates='professional')

    def __repr__(self):
        return f'<Professional {self.name}>'
