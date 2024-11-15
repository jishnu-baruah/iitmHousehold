from flask import Blueprint, jsonify
from app.models.user import Professional, Customer, Admin
from app import db

test_bp = Blueprint('test', __name__)

@test_bp.route('/create-test-data')
def create_test_data():
    try:
        # Create a professional
        prof = Professional(
            username="john_plumber",
            email="john@example.com",
            role="professional",
            service_type="plumbing",
            experience=5,
            description="Professional plumber with 5 years experience",
            qualification="Certified Plumber",
            hourly_rate=50.0,
            location="New York",
            pincode="10001",
            languages="English,Spanish",
            specializations='["Emergency Plumbing", "Installation", "Maintenance"]',
            available_hours='{"weekdays": "9:00-17:00", "weekends": "10:00-15:00"}'
        )
        prof.set_password("test123")
        db.session.add(prof)

        # Create a customer
        cust = Customer(
            username="alice_customer",
            email="alice@example.com",
            role="customer",
            address="123 Main St",
            phone="1234567890",
            default_location="New York",
            default_pincode="10001",
            preferred_payment_method="credit_card"
        )
        cust.set_password("test123")
        db.session.add(cust)

        # Create test admin if not exists
        admin = Admin.query.filter_by(username="admin").first()
        if not admin:
            admin = Admin(
                username="admin",
                email="admin@example.com",
                role="admin"
            )
            admin.set_password("admin123")
            db.session.add(admin)

        db.session.commit()

        # Test professional search
        test_search = Professional.search(
            service_type="plumbing",
            location="New York",
            pincode="10001"
        ).all()

        # Test professional rating update
        prof.update_rating(4.5)

        # Test customer favorites
        cust.add_to_favorites(prof.id)

        return jsonify({
            "message": "Test data created successfully",
            "professional": prof.to_dict(),
            "customer": cust.to_dict(),
            "search_results": [p.to_dict() for p in test_search]
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@test_bp.route('/test-search')
def test_search():
    try:
        # Test different search scenarios
        results = {
            "by_service": Professional.search(service_type="plumbing").all(),
            "by_location": Professional.search(location="New York").all(),
            "by_rating": Professional.search(min_rating=4.0).all(),
            "by_language": Professional.search(languages="Spanish").all(),
            "by_price": Professional.search(max_price=60.0).all()
        }

        return jsonify({
            "search_results": {
                key: [p.to_dict() for p in value]
                for key, value in results.items()
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@test_bp.route('/user-stats')
def user_stats():
    try:
        admin = Admin.query.first()
        if admin:
            stats = admin.get_dashboard_stats()
            return jsonify(stats)
        return jsonify({"error": "Admin not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
