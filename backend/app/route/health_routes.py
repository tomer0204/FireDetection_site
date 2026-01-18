from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

@health_bp.route("/", methods=["GET"])
def root():
    return jsonify({"status": "ok"}), 200

@health_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200
