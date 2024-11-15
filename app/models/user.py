from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager
from datetime import datetime
from sqlalchemy import or_

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    profile_pic = db.Column(db.String(200))
    last_active = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="online")  # online/offline/busy
    notifications_enabled = db.Column(db.Boolean, default=True)
    
    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": role
    }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        self.last_login = datetime.utcnow()
        self.last_active = datetime.utcnow()
        db.session.commit()

    def update_status(self, status):
        valid_statuses = ["online", "offline", "busy"]
        if status in valid_statuses:
            self.status = status
            self.last_active = datetime.utcnow()
            db.session.commit()

    def toggle_notifications(self):
        self.notifications_enabled = not self.notifications_enabled
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "is_active": self.is_active,
            "last_login": self.last_login.strftime("%Y-%m-%d %H:%M:%S") if self.last_login else None,
            "status": self.status,
            "last_active": self.last_active.strftime("%Y-%m-%d %H:%M:%S") if self.last_active else None
        }

class Admin(User):
    __mapper_args__ = {
        "polymorphic_identity": "admin"
    }

    def get_dashboard_stats(self):
        from app.models.service import Service
        from app.models.request import ServiceRequest
        
        # Get current datetime
        now = datetime.utcnow()
        
        return {
            "total_users": User.query.count(),
            "total_professionals": Professional.query.count(),
            "total_customers": Customer.query.count(),
            "total_services": Service.query.count(),
            "pending_verifications": Professional.query.filter_by(is_verified=False).count(),
            "active_requests": ServiceRequest.query.filter_by(status="assigned").count(),
            "online_professionals": Professional.query.filter_by(status="online").count(),
            "total_earnings": db.session.query(db.func.sum(Professional.total_earnings)).scalar() or 0,
            "recent_signups": User.query.filter(User.created_at >= now.date()).count(),
            "pending_reviews": ServiceRequest.query.filter_by(status="completed")
                             .filter_by(rating=None).count()
        }

    def verify_professional(self, professional_id):
        professional = Professional.query.get(professional_id)
        if professional:
            professional.is_verified = True
            db.session.commit()
            return True
        return False

    def block_user(self, user_id):
        user = User.query.get(user_id)
        if user:
            user.is_active = False
            db.session.commit()
            return True
        return False

class Professional(User):
    __tablename__ = "professional"
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    service_type = db.Column(db.String(50))
    experience = db.Column(db.Integer)
    description = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)
    is_available = db.Column(db.Boolean, default=True)
    qualification = db.Column(db.String(200))
    hourly_rate = db.Column(db.Float, default=0.0)
    total_earnings = db.Column(db.Float, default=0.0)
    rating = db.Column(db.Float, default=0.0)
    total_ratings = db.Column(db.Integer, default=0)
    location = db.Column(db.String(200))
    pincode = db.Column(db.String(10))
    available_hours = db.Column(db.String(200))
    service_area = db.Column(db.String(500))  # JSON string of service areas
    languages = db.Column(db.String(200))  # Comma-separated languages
    specializations = db.Column(db.String(500))  # JSON string of specializations
    certifications = db.Column(db.String(500))  # JSON string of certifications
    completion_rate = db.Column(db.Float, default=0.0)
    response_time = db.Column(db.Integer)  # Average response time in minutes
    
    service_requests = db.relationship("ServiceRequest", 
                                     back_populates="professional",
                                     lazy="dynamic",
                                     cascade="all, delete-orphan")

    __mapper_args__ = {
        "polymorphic_identity": "professional"
    }

    @classmethod
    def search(cls, service_type=None, location=None, pincode=None, 
              min_rating=None, languages=None, max_price=None):
        query = cls.query.filter_by(is_verified=True, is_available=True)
        
        if service_type:
            query = query.filter_by(service_type=service_type)
        
        if location:
            query = query.filter(
                or_(
                    cls.location.ilike(f"%{location}%"),
                    cls.service_area.ilike(f"%{location}%")
                )
            )
            
        if pincode:
            query = query.filter_by(pincode=pincode)
            
        if min_rating is not None:
            query = query.filter(cls.rating >= min_rating)
            
        if languages:
            query = query.filter(cls.languages.ilike(f"%{languages}%"))
            
        if max_price is not None:
            query = query.filter(cls.hourly_rate <= max_price)
            
        return query.order_by(cls.rating.desc())

    def update_rating(self, new_rating):
        if self.total_ratings == 0:
            self.rating = new_rating
        else:
            self.rating = ((self.rating * self.total_ratings) + new_rating) / (self.total_ratings + 1)
        self.total_ratings += 1
        self.update_completion_rate()
        db.session.commit()

    def get_active_requests(self):
        return self.service_requests.filter_by(status="assigned").all()

    def update_completion_rate(self):
        total_requests = self.service_requests.count()
        if total_requests > 0:
            completed = self.service_requests.filter_by(status="completed").count()
            self.completion_rate = (completed / total_requests) * 100
            db.session.commit()

    def update_earnings(self, amount):
        self.total_earnings += amount
        db.session.commit()

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "service_type": self.service_type,
            "experience": self.experience,
            "description": self.description,
            "is_verified": self.is_verified,
            "is_available": self.is_available,
            "qualification": self.qualification,
            "hourly_rate": self.hourly_rate,
            "rating": self.rating,
            "total_ratings": self.total_ratings,
            "location": self.location,
            "completion_rate": self.completion_rate,
            "response_time": self.response_time,
            "languages": self.languages,
            "specializations": self.specializations
        })
        return data

class Customer(User):
    __tablename__ = "customer"
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    default_location = db.Column(db.String(200))
    preferred_payment_method = db.Column(db.String(50))
    total_spent = db.Column(db.Float, default=0.0)
    favorite_professionals = db.Column(db.String(500))  # JSON string of professional IDs
    default_pincode = db.Column(db.String(10))
    
    service_requests = db.relationship("ServiceRequest", 
                                     back_populates="customer",
                                     lazy="dynamic",
                                     cascade="all, delete-orphan")

    __mapper_args__ = {
        "polymorphic_identity": "customer"
    }

    def get_active_requests(self):
        return self.service_requests.filter(
            ServiceRequest.status.in_(["requested", "assigned"])
        ).all()

    def get_completed_requests(self):
        return self.service_requests.filter_by(status="completed").all()

    def get_pending_payments(self):
        return self.service_requests.filter(
            ServiceRequest.status == "completed",
            ServiceRequest.payment_status == "pending"
        ).all()

    def add_to_favorites(self, professional_id):
        import json
        favorites = json.loads(self.favorite_professionals or "[]")
        if professional_id not in favorites:
            favorites.append(professional_id)
            self.favorite_professionals = json.dumps(favorites)
            db.session.commit()

    def remove_from_favorites(self, professional_id):
        import json
        favorites = json.loads(self.favorite_professionals or "[]")
        if professional_id in favorites:
            favorites.remove(professional_id)
            self.favorite_professionals = json.dumps(favorites)
            db.session.commit()

    def update_total_spent(self, amount):
        self.total_spent += amount
        db.session.commit()

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "address": self.address,
            "phone": self.phone,
            "default_location": self.default_location,
            "preferred_payment_method": self.preferred_payment_method,
            "total_spent": self.total_spent,
            "default_pincode": self.default_pincode
        })
        return data

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
