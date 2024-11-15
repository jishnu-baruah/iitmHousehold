from app.api import bp
from flask import jsonify

@bp.route("/users")
def get_users():
    return jsonify({"message": "Users list"})
