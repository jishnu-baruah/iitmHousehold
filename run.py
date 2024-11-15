from app import create_app, db
from app.models.user import User, Admin, Professional, Customer
from app.models.service import Service
from app.models.request import ServiceRequest

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "Admin": Admin,
        "Professional": Professional,
        "Customer": Customer,
        "Service": Service,
        "ServiceRequest": ServiceRequest
    }

if __name__ == "__main__":
    app.run(debug=True)
