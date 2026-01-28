from flask import jsonify
from flask_jwt_extended import jwt_required
from app.service.track_service import get_tracks_by_camera

@jwt_required()
def get_tracks_by_camera_controller(camera_id):
    tracks = get_tracks_by_camera(camera_id)
    return jsonify([
        {
            "track_id": t.track_id,
            "camera_id": t.camera_id,
            "created_at": t.created_at,
            "updated_at": t.updated_at
        }
        for t in tracks
    ])
