from flask import Blueprint

favicon_bp = Blueprint("favicon", __name__)

@favicon_bp.route("/favicon.ico")
def favicon():
    return "", 204
