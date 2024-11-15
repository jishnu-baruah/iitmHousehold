from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    users = User.query.all()
    print(f"Number of users in database: {len(users)}")
    for user in users:
        print(f"User: {user.username}, Role: {user.role}")
