from app import create_app, db
from app.models.user import Admin

app = create_app()
with app.app_context():
    # Check if admin already exists
    admin = Admin.query.filter_by(username="admin").first()
    if not admin:
        admin = Admin(username="admin", email="admin@example.com")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
    else:
        print("Admin user already exists!")
