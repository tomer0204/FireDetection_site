import os
import threading
from flask import request
from flask_socketio import join_room, leave_room
from flask_jwt_extended import verify_jwt_in_request
from app.extensions import socketio
from app.service.camera_stream_service import get_stream
from app.service.inference_socket_client import InferenceSocketClient

INFERENCE_WS_URL = os.getenv("INFERENCE_URL", "http://orchestrator:5001").rstrip("/")

WORKERS = {}
WORKERS_LOCK = threading.Lock()

def _room_has_listeners(room: str) -> bool:
    rooms = socketio.server.manager.rooms
    ns_rooms = rooms.get("/", {})
    participants = ns_rooms.get(room)
    return bool(participants)

def register_stream_ws(app):

    @socketio.on("connect")
    def on_connect():
        verify_jwt_in_request()

    @socketio.on("join_stream")
    def on_join_stream(data):
        verify_jwt_in_request()

        stream_id = int(data["stream_id"])
        room = f"stream:{stream_id}"
        join_room(room)

        with WORKERS_LOCK:
            if stream_id not in WORKERS:
                WORKERS[stream_id] = socketio.start_background_task(stream_worker, app, stream_id, room)

        socketio.emit("joined_stream", {"stream_id": stream_id})

    @socketio.on("leave_stream")
    def on_leave_stream(data):
        verify_jwt_in_request()

        stream_id = int(data["stream_id"])
        room = f"stream:{stream_id}"
        leave_room(room)
        socketio.emit("left_stream", {"stream_id": stream_id})

def stream_worker(app, stream_id: int, room: str):
    with app.app_context():
        stream = get_stream(stream_id)
        if not stream or not stream.is_active:
            socketio.emit("stream_error", {"error": "STREAM_NOT_ACTIVE"}, room=room)
            with WORKERS_LOCK:
                WORKERS.pop(stream_id, None)
            return

        run_id = stream.run_id
        fps = int(stream.fps) if stream.fps else 10

    client = InferenceSocketClient(INFERENCE_WS_URL)

    frame_lock = threading.Lock()
    last_frame = {"data": None}

    def on_infer_frame(frame_bytes):
        with frame_lock:
            last_frame["data"] = frame_bytes

    client.on_frame(on_infer_frame)

    try:
        client.subscribe(run_id)

        delay = 1.0 / max(1, fps)

        while True:
            if not _room_has_listeners(room):
                break

            with app.app_context():
                s = get_stream(stream_id)
                if not s or not s.is_active:
                    break

            data = None
            with frame_lock:
                data = last_frame["data"]
                last_frame["data"] = None

            if data:
                socketio.emit("frame", data, room=room)

            socketio.sleep(delay)

    finally:
        try:
            client.unsubscribe(run_id)
        except Exception:
            pass

        client.disconnect_client()

        with WORKERS_LOCK:
            WORKERS.pop(stream_id, None)
