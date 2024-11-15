from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.professional import bp
from app.models.request import ServiceRequest
from app import db
from datetime import datetime

@bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.role == "professional":
        flash("Access denied", "danger")
        return redirect(url_for("auth.login"))
    
    # Get requests statistics
    pending_requests = ServiceRequest.query.filter_by(
        professional_id=current_user.id,
        status="requested"
    ).count()
    
    active_requests = ServiceRequest.query.filter_by(
        professional_id=current_user.id,
        status="assigned"
    ).all()
    
    completed_requests = ServiceRequest.query.filter_by(
        professional_id=current_user.id,
        status="completed"
    ).order_by(ServiceRequest.date_of_completion.desc()).limit(5).all()

    # Get recent service requests
    recent_requests = ServiceRequest.query.filter_by(
        service_id=current_user.service_type
    ).filter_by(status="requested").all()

    return render_template('professional/dashboard.html',
                         pending_requests=pending_requests,
                         active_requests=active_requests,
                         completed_requests=completed_requests,
                         recent_requests=recent_requests)

@bp.route('/request/<int:request_id>/accept', methods=['POST'])
@login_required
def accept_request(request_id):
    if not current_user.role == "professional":
        flash("Access denied", "danger")
        return redirect(url_for("auth.login"))
    
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    if service_request.status != "requested":
        flash("This request cannot be accepted", "danger")
        return redirect(url_for("professional.dashboard"))
    
    service_request.professional_id = current_user.id
    service_request.status = "assigned"
    db.session.commit()
    
    flash("Service request accepted successfully", "success")
    return redirect(url_for("professional.dashboard"))

@bp.route('/request/<int:request_id>/complete', methods=['POST'])
@login_required
def complete_request(request_id):
    if not current_user.role == "professional":
        flash("Access denied", "danger")
        return redirect(url_for("auth.login"))
    
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    if service_request.professional_id != current_user.id:
        flash("Access denied", "danger")
        return redirect(url_for("professional.dashboard"))
    
    if service_request.status != "assigned":
        flash("This request cannot be completed", "danger")
        return redirect(url_for("professional.dashboard"))
    
    service_request.status = "completed"
    service_request.date_of_completion = datetime.utcnow()
    db.session.commit()
    
    flash("Service request marked as completed", "success")
    return redirect(url_for("professional.dashboard"))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if not current_user.role == "professional":
        flash("Access denied", "danger")
        return redirect(url_for("auth.login"))
    
    if request.method == 'POST':
        current_user.description = request.form.get('description')
        current_user.experience = request.form.get('experience')
        current_user.qualification = request.form.get('qualification')
        current_user.hourly_rate = float(request.form.get('hourly_rate'))
        current_user.location = request.form.get('location')
        current_user.available_hours = request.form.get('available_hours')
        db.session.commit()
        flash("Profile updated successfully", "success")
        return redirect(url_for("professional.profile"))
    
    return render_template('professional/profile.html')

@bp.route('/requests')
@login_required
def requests():
    if not current_user.role == "professional":
        flash("Access denied", "danger")
        return redirect(url_for("auth.login"))
    
    active_requests = ServiceRequest.query.filter_by(
        professional_id=current_user.id,
        status="assigned"
    ).all()
    
    pending_requests = ServiceRequest.query.filter_by(
        service_id=current_user.service_type,
        status="requested"
    ).all()
    
    completed_requests = ServiceRequest.query.filter_by(
        professional_id=current_user.id,
        status="completed"
    ).order_by(ServiceRequest.date_of_completion.desc()).all()
    
    return render_template('professional/requests.html',
                         active_requests=active_requests,
                         pending_requests=pending_requests,
                         completed_requests=completed_requests)
