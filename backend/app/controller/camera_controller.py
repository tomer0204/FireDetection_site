from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.service.camera_service import list_cameras, create_camera, get_camera_by_id

def camera_to_dict(c):
    return {
        "camera_id": c.camera_id,
        "name": c.name,
        "lat": c.lat,
        "lng": c.lng,
        "is_enabled": c.is_enabled
    }

@jwt_required()
def get_cameras_controller():
    cameras = list_cameras()
    return jsonify([camera_to_dict(c) for c in cameras]), 200

@jwt_required()
def get_camera_controller(camera_id: int):
    c = get_camera_by_id(camera_id)
    if not c:
        return jsonify({"error": "NOT_FOUND", "message": "Camera not found"}), 404
    return jsonify(camera_to_dict(c)), 200

@jwt_required()
def create_camera_controller():
    data = request.get_json() or {}
    name = data.get("name")
    lat = data.get("lat")
    lng = data.get("lng")

    if not name or lat is None or lng is None:
        return jsonify({"error": "VALIDATION_ERROR", "message": "name, lat, lng are required"}), 400

    camera = create_camera(name=name, lat=float(lat), lng=float(lng))
    return jsonify(camera_to_dict(camera)), 201
