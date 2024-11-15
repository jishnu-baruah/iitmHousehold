from app.api import bp
from flask import jsonify

@bp.route("/requests")
def get_requests():
    return jsonify({"message": "Requests list"})
