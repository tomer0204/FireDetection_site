from flask import Blueprint
from app.controller.camera_controller import (
    get_cameras_controller,
    create_camera_controller,
    get_camera_controller
)

camera_bp = Blueprint("cameras", __name__)

camera_bp.route("/cameras", methods=["GET"])(get_cameras_controller)
camera_bp.route("/cameras", methods=["POST"])(create_camera_controller)
camera_bp.route("/cameras/<int:camera_id>", methods=["GET"])(get_camera_controller)
