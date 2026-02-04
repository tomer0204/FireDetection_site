from flask import Blueprint
from app.controller.camera_stream_controller import (
    create_stream_controller,
    get_stream_controller,
    stop_stream_controller,
    list_camera_streams_controller
)

stream_bp = Blueprint("streams", __name__)

stream_bp.route("/streams", methods=["POST"])(create_stream_controller)
stream_bp.route("/streams/<int:stream_id>", methods=["GET"])(get_stream_controller)
stream_bp.route("/streams/<int:stream_id>/stop", methods=["POST"])(stop_stream_controller)
stream_bp.route("/cameras/<int:camera_id>/streams", methods=["GET"])(list_camera_streams_controller)
