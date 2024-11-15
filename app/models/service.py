from app import db
from datetime import datetime
from sqlalchemy import or_

class Service(db.Model):
    __tablename__ = "service"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    base_price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.Integer)  # in minutes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # New fields for enhanced search
    service_type = db.Column(db.String(50))
    tags = db.Column(db.String(200))  # Comma-separated tags
    availability = db.Column(db.String(200))  # JSON string for availability schedule
    min_price = db.Column(db.Float)  # Minimum service price
    max_price = db.Column(db.Float)  # Maximum service price
    rating = db.Column(db.Float, default=0.0)
    total_ratings = db.Column(db.Integer, default=0)
    location_coverage = db.Column(db.String(500))  # JSON string of covered areas
    
    # Relationships
    service_requests = db.relationship("ServiceRequest", 
                                     back_populates="service",
                                     lazy="dynamic",
                                     cascade="all, delete-orphan")

    @classmethod
    def search(cls, query=None, service_type=None, location=None, 
              min_price=None, max_price=None, rating=None):
        """
        Advanced search method for services
        """
        search_query = cls.query.filter_by(is_active=True)

        if query:
            search_query = search_query.filter(
                or_(
                    cls.name.ilike(f"%{query}%"),
                    cls.description.ilike(f"%{query}%"),
                    cls.tags.ilike(f"%{query}%")
                )
            )

        if service_type:
            search_query = search_query.filter_by(service_type=service_type)

        if min_price is not None:
            search_query = search_query.filter(cls.base_price >= min_price)

        if max_price is not None:
            search_query = search_query.filter(cls.base_price <= max_price)

        if rating:
            search_query = search_query.filter(cls.rating >= rating)

        if location:
            search_query = search_query.filter(
                cls.location_coverage.ilike(f"%{location}%")
            )

        return search_query

    def update_rating(self, new_rating):
        """
        Update service rating with a new rating value
        """
        if self.total_ratings == 0:
            self.rating = new_rating
        else:
            self.rating = ((self.rating * self.total_ratings) + new_rating) / (self.total_ratings + 1)
        self.total_ratings += 1
        db.session.commit()

    def to_dict(self):
        """
        Convert service to dictionary for API responses
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "service_type": self.service_type,
            "base_price": self.base_price,
            "min_price": self.min_price,
            "max_price": self.max_price,
            "time_required": self.time_required,
            "rating": self.rating,
            "total_ratings": self.total_ratings,
            "is_active": self.is_active,
            "availability": self.availability,
            "location_coverage": self.location_coverage,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_available_professionals(self, location=None):
        """
        Get list of available professionals for this service
        """
        from app.models.user import Professional
        query = Professional.query.filter_by(
            service_type=self.service_type,
            is_verified=True,
            is_available=True
        )
        
        if location:
            query = query.filter(Professional.location.ilike(f"%{location}%"))
        
        return query.all()
