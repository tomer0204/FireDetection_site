from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
    jwt_required,
    get_jwt_identity
)
from app.controller.auth_controller import login, register
from app.model.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register_route():
    user = register(request.json or {})
    return jsonify({
        "user": {
            "id": user.user_id,
            "email": user.email,
            "username": user.username,
            "role": user.role.value,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login_route():
    user, access_token, refresh_token = login(request.json or {})

    response = jsonify({
        "user": {
            "id": user.user_id,
            "email": user.email,
            "username": user.username,
            "role": user.role.value,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
    })

    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response, 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me_route():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        return jsonify({"error": "UNAUTHORIZED", "message": "User not found"}), 401

    return jsonify({
        "user": {
            "id": user.user_id,
            "email": user.email,
            "username": user.username,
            "role": user.role.value,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
    }), 200

@auth_bp.route("/logout", methods=["POST"])
def logout_route():
    response = jsonify({"message": "Logged out"})
    unset_jwt_cookies(response)
    return response, 200
