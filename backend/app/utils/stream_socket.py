from flask_socketio import join_room, leave_room
from app.extensions import socketio
from app.service.inference_socket_client import inference_client
from app.model.camera_stream import CameraStream

ACTIVE_STREAMS = {}

def register_stream_ws(app):

    @socketio.on("join_stream")
    def on_join(data):
        stream_id = int(data["stream_id"])
        room = f"stream:{stream_id}"
        join_room(room)

        if stream_id in ACTIVE_STREAMS:
            return

        stream = CameraStream.query.get(stream_id)
        if not stream or not stream.is_active:
            socketio.emit("stream_error", {"error": "NO_ACTIVE_STREAM"}, room=room)
            return

        run_id = str(stream.run_id)

        def emit_frame(frame_bytes: bytes, frame_index: int | None):
            socketio.emit("frame", frame_bytes, room=room)

        def emit_detections(payload: dict):
            socketio.emit("detections", payload, room=room)

        inference_client.subscribe(
            run_id=run_id,
            on_frame=emit_frame,
            on_detections=emit_detections
        )

        ACTIVE_STREAMS[stream_id] = run_id

    @socketio.on("leave_stream")
    def on_leave(data):
        stream_id = int(data["stream_id"])
        room = f"stream:{stream_id}"
        leave_room(room)

        run_id = ACTIVE_STREAMS.pop(stream_id, None)
        if run_id:
            inference_client.unsubscribe(run_id)
