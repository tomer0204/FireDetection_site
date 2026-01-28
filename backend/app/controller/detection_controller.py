from flask import jsonify
from flask_jwt_extended import jwt_required
from app.service.detection_service import get_detections_by_camera

@jwt_required()
def get_detections_by_camera_controller(camera_id):
    detections = get_detections_by_camera(camera_id)
    return jsonify([
        {
            "detection_id": d.detection_id,
            "camera_id": d.camera_id,
            "track_id": d.track_id,
            "coordinates": d.coordinates,
            "created_at": d.created_at,
            "updated_at": d.updated_at
        }
        for d in detections
    ])
