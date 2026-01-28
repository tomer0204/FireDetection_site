from flask import Blueprint
from app.controller.camera_stream_controller import (
    get_camera_stream_controller,
    start_camera_stream_controller,
    stop_camera_stream_controller,
    camera_live_controller
)

stream_bp = Blueprint("camera_streams", __name__)

stream_bp.route("/cameras/<int:camera_id>/stream", methods=["GET"])(get_camera_stream_controller)
stream_bp.route("/cameras/<int:camera_id>/stream/start", methods=["POST"])(start_camera_stream_controller)
stream_bp.route("/cameras/<int:camera_id>/stream/stop", methods=["POST"])(stop_camera_stream_controller)
stream_bp.route("/cameras/<int:camera_id>/live", methods=["GET"])(camera_live_controller)
