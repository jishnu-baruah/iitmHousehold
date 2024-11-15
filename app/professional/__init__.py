from flask import Blueprint

bp = Blueprint("professional", __name__, url_prefix="/professional")

# Import routes after Blueprint creation to avoid circular imports
from app.professional.routes import *

# Register error handlers
@bp.errorhandler(404)
def not_found_error(error):
    return {"error": "Resource not found"}, 404

@bp.errorhandler(500)
def internal_error(error):
    from app import db
    db.session.rollback()
    return {"error": "Internal server error"}, 500

# Register before request handler to check professional access
from flask_login import current_user
from functools import wraps
from flask import redirect, url_for, flash

def professional_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "professional":
            flash("Access denied. Professional rights required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

# Register profile completion check
def check_profile_completion():
    if current_user.is_authenticated and current_user.role == "professional":
        required_fields = [
            current_user.service_type,
            current_user.experience,
            current_user.description,
            current_user.qualification,
            current_user.hourly_rate,
            current_user.location,
            current_user.available_hours
        ]
        if not all(required_fields):
            flash("Please complete your profile to access all features", "warning")
            return redirect(url_for("professional.complete_profile"))

@bp.before_request
def before_request():
    if current_user.is_authenticated and current_user.role == "professional":
        current_user.update_last_login()
        if not current_user.is_verified:
            flash("Your account is pending verification. Some features may be limited.", "warning")

# Context processors for template access
@bp.context_processor
def utility_processor():
    def get_completion_percentage():
        if not current_user.is_authenticated or current_user.role != "professional":
            return 0
            
        fields = {
            'service_type': 15,
            'experience': 10,
            'description': 15,
            'qualification': 15,
            'hourly_rate': 10,
            'location': 10,
            'available_hours': 10,
            'languages': 5,
            'specializations': 10
        }
        
        completed = sum(fields[field] for field in fields 
                       if getattr(current_user, field, None))
        return completed

    def get_active_requests_count():
        if not current_user.is_authenticated or current_user.role != "professional":
            return 0
        return current_user.get_active_requests().count()

    return dict(
        get_completion_percentage=get_completion_percentage,
        get_active_requests_count=get_active_requests_count,
        is_verified=lambda: current_user.is_verified if hasattr(current_user, 'is_verified') else False
    )

# Signal handlers for professional events
from app import db
from datetime import datetime

def on_service_completed(sender, professional_id):
    professional = sender.query.get(professional_id)
    if professional:
        professional.update_completion_rate()
        db.session.commit()

def on_rating_received(sender, professional_id, rating):
    professional = sender.query.get(professional_id)
    if professional:
        professional.update_rating(rating)
        db.session.commit()
