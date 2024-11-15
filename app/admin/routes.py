from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.admin import bp
from app.models.user import User, Professional, Customer
from app.models.service import Service
from app.models.request import ServiceRequest
from app.forms.service import ServiceForm
from app import db

# ... [keep existing dashboard routes] ...

@bp.route("/services")
@login_required
def services():
    if not current_user.role == "admin":
        flash("Access denied", "danger")
        return redirect(url_for("auth.login"))
    
    services = Service.query.all()
    return render_template("admin/services.html", services=services)

@bp.route("/service/create", methods=["GET", "POST"])
@login_required
def create_service():
    if not current_user.role == "admin":
        flash("Access denied", "danger")
        return redirect(url_for("auth.login"))
    
    form = ServiceForm()
    if form.validate_on_submit():
        service = Service(
            name=form.name.data,
            description=form.description.data,
            base_price=form.base_price.data,
            time_required=form.time_required.data
        )
        db.session.add(service)
        db.session.commit()
        flash("Service created successfully!", "success")
        return redirect(url_for("admin.services"))
    
    return render_template("admin/create_service.html", form=form)

@bp.route("/service/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_service(id):
    if not current_user.role == "admin":
        flash("Access denied", "danger")
        return redirect(url_for("auth.login"))
    
    service = Service.query.get_or_404(id)
    form = ServiceForm(obj=service)
    
    if form.validate_on_submit():
        service.name = form.name.data
        service.description = form.description.data
        service.base_price = form.base_price.data
        service.time_required = form.time_required.data
        db.session.commit()
        flash("Service updated successfully!", "success")
        return redirect(url_for("admin.services"))
    
    return render_template("admin/edit_service.html", form=form, service=service)

@bp.route("/service/<int:id>/delete", methods=["POST"])
@login_required
def delete_service(id):
    if not current_user.role == "admin":
        flash("Access denied", "danger")
        return redirect(url_for("auth.login"))
    
    service = Service.query.get_or_404(id)
    service.is_active = False
    db.session.commit()
    flash("Service has been deleted!", "success")
    return redirect(url_for("admin.services"))
