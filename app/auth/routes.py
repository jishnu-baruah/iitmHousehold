from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.auth import bp
from app.forms.auth import LoginForm, RegistrationForm
from app.models.user import User, Customer, Professional
from app import db

@bp.route("/")
def index():
    return render_template("index.html", title="Home")

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.index"))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password", "danger")
            return redirect(url_for("auth.login"))
        
        login_user(user)
        next_page = request.args.get("next")
        if not next_page or not next_page.startswith("/"):
            if user.role == "admin":
                next_page = url_for("admin.dashboard")
            elif user.role == "professional":
                next_page = url_for("professional.dashboard")
            else:
                next_page = url_for("customer.dashboard")
        return redirect(next_page)
    
    return render_template("auth/login.html", title="Sign In", form=form)

@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("auth.index"))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            if form.role.data == "professional":
                user = Professional(
                    username=form.username.data,
                    email=form.email.data,
                    role="professional"
                )
            else:
                user = Customer(
                    username=form.username.data,
                    email=form.email.data,
                    role="customer"
                )
            
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            
            flash("Congratulations, you are now registered!", "success")
            return redirect(url_for("auth.login"))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Registration failed: {str(e)}", "danger")
            print(f"Registration error: {str(e)}")  # For debugging
            return redirect(url_for("auth.register"))
    
    # If form validation failed, show the errors
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{field}: {error}", "danger")
    
    return render_template("auth/register.html", title="Register", form=form)

@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.index"))
