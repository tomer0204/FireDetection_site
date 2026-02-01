from flask import request, jsonify, Response
from flask_jwt_extended import jwt_required
from app.service.camera_stream_service import (
    create_stream,
    stop_stream,
    get_stream,
    get_active_streams_for_camera,
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
        "started_at": s.started_at.isoformat(),
        "ended_at": s.ended_at.isoformat() if s.ended_at else None,
        "is_active": s.is_active
    }


@jwt_required()
def create_stream_controller():
    data = request.get_json() or {}
    camera_id = int(data["camera_id"])
    fps = int(data.get("fps", 10))

    stream = create_stream(camera_id, fps)
    return jsonify(stream_to_dict(stream)), 201

@jwt_required()
def get_stream_controller(stream_id: int):
    stream = get_stream(stream_id)
    if not stream:
        return jsonify({"error": "NOT_FOUND"}), 404
    return jsonify(stream_to_dict(stream)), 200

@jwt_required()
def stop_stream_controller(stream_id: int):
    stream = stop_stream(stream_id)
    if not stream:
        return jsonify({"error": "NO_ACTIVE_STREAM"}), 400
    return jsonify({"stopped": True}), 200

@jwt_required()
def live_stream_controller(stream_id: int):
    return Response(
        live_frame_generator(stream_id),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@jwt_required()
def list_camera_streams_controller(camera_id: int):
    streams = get_active_streams_for_camera(camera_id)
    return jsonify([stream_to_dict(s) for s in streams]), 200
