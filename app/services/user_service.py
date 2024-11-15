from app.models.user import User, Admin, Professional, Customer
from app import db

class UserService:
    @staticmethod
    def create_user(data, role):
        if role == "admin":
            user = Admin(username=data["username"], email=data["email"])
        elif role == "professional":
            user = Professional(
                username=data["username"],
                email=data["email"],
                service_type=data["service_type"],
                experience=data["experience"],
                description=data["description"]
            )
        else:
            user = Customer(
                username=data["username"],
                email=data["email"],
                address=data["address"],
                phone=data["phone"]
            )
        
        user.set_password(data["password"])
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def verify_professional(professional_id):
        professional = Professional.query.get(professional_id)
        if professional:
            professional.is_verified = True
            db.session.commit()
            return True
        return False

    @staticmethod
    def block_user(user_id):
        user = User.query.get(user_id)
        if user:
            user.is_active = False
            db.session.commit()
            return True
        return False
