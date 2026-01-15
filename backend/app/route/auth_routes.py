from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
    jwt_required,
    get_jwt_identity,
)
from app.controller.auth_controller import register, login
from app.extensions import limiter
from app.service.auth_service import get_user_by_id

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5/minute")
def register_route():
    user = register(request.get_json(force=True))
    return jsonify({"user_id": user.user_id, "email": user.email, "role": user.role}), 201

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10/minute")
def login_route():
    user, access_token, refresh_token = login(request.get_json(force=True))
    resp = jsonify({"message": "ok", "user_id": user.user_id, "email": user.email, "role": user.role})
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp, 200

@auth_bp.route("/logout", methods=["POST"])
def logout_route():
    resp = jsonify({"message": "ok"})
    unset_jwt_cookies(resp)
    return resp, 200

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_route():
    user_id = get_jwt_identity()
    user = get_user_by_id(user_id)
    if not user or not user.is_active:
        return jsonify({"error": "UNAUTHORIZED", "message": "Unauthorized"}), 401
    from flask_jwt_extended import create_access_token
    access_token = create_access_token(identity=user.user_id, additional_claims={"role": user.role})
    resp = jsonify({"message": "ok"})
    set_access_cookies(resp, access_token)
    return resp, 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me_route():
    user_id = get_jwt_identity()
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "NOT_FOUND", "message": "User not found"}), 404
    return jsonify({"user_id": user.user_id, "email": user.email, "role": user.role, "is_active": user.is_active}), 200
