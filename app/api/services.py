from app.api import bp
from flask import jsonify

@bp.route("/services")
def get_services():
    return jsonify({"message": "Services list"})
