from flask import request, jsonify, Response
from flask_jwt_extended import jwt_required
from app.service.camera_stream_service import (
    get_active_stream,
    start_camera_stream,
    stop_camera_stream,
    live_frame_generator
)

def stream_to_dict(s):
    return {
        "stream_id": s.stream_id,
        "camera_id": s.camera_id,
        "run_id": s.run_id,
        "source_type": s.source_type,
        "source_ref": s.source_ref,
        "fps": s.fps,
        "s3_prefix": s.s3_prefix,
        "started_at": s.started_at.isoformat() if s.started_at else None,
        "ended_at": s.ended_at.isoformat() if s.ended_at else None,
        "is_active": s.is_active
    }

@jwt_required()
def get_camera_stream_controller(camera_id: int):
    s = get_active_stream(camera_id)
    if not s:
        return jsonify({"is_active": False, "stream": None}), 200
    return jsonify({"is_active": True, "stream": stream_to_dict(s)}), 200

@jwt_required()
def start_camera_stream_controller(camera_id: int):
    data = request.get_json() or {}
    fps = int(data.get("fps", 17))
    source_ref = data.get("source_ref", "minio")

    s = start_camera_stream(camera_id=camera_id, source_ref=source_ref, fps=fps)
    return jsonify({"stream": stream_to_dict(s)}), 201

@jwt_required()
def stop_camera_stream_controller(camera_id: int):
    s = stop_camera_stream(camera_id)
    if not s:
        return jsonify({"error": "NO_ACTIVE_STREAM"}), 400
    return jsonify({"stopped": True}), 200

@jwt_required()
def camera_live_controller(camera_id: int):
    return Response(
        live_frame_generator(camera_id),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )
