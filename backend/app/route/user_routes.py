from flask import Blueprint, request, jsonify
from app.controller.user import register_user

user_bp = Blueprint("users", __name__)

@user_bp.route("/register", methods=["POST"])
def register():
    user = register_user(request.json)
    return jsonify({"id": user.id}), 201
