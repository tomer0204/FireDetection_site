from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.model.camera import Camera

camera_bp = Blueprint("cameras", __name__)

@camera_bp.route("/cameras", methods=["GET"])
@jwt_required()
def get_cameras():
    cameras = Camera.query.all()

    return jsonify([
        {
            "camera_id": c.camera_id,
            "is_active": c.is_active
        }
        for c in cameras
    ])
