import os
import threading
import socketio

INFERENCE_WS_URL = os.getenv(
    "INFERENCE_WS_URL",
    os.getenv("INFERENCE_URL", "http://orchestrator:5001")
).rstrip("/")


class InferenceSocketClient:
    def __init__(self):
        self.sio = socketio.Client(reconnection=True)
        self._lock = threading.Lock()
        self._callbacks = {}

        @self.sio.event
        def connect():
            print("[Inference WS] connected")

        @self.sio.event
        def disconnect():
            print("[Inference WS] disconnected")

        @self.sio.on("infer_frame")
        def on_infer_frame(payload):
            if not isinstance(payload, dict):
                return

            run_id = str(payload.get("run_id", ""))
            frame = payload.get("frame")
            frame_index = payload.get("frame_index")

            if not run_id or not isinstance(frame, (bytes, bytearray)):
                return

            with self._lock:
                cb = self._callbacks.get(run_id)


            if cb and cb.get("on_frame"):
                cb["on_frame"](bytes(frame), frame_index)

        @self.sio.on("infer_result")
        def on_infer_result(payload):
            if not isinstance(payload, dict):
                return

            run_id = str(payload.get("run_id", ""))
            if not run_id:
                return

            with self._lock:
                cb = self._callbacks.get(run_id)

            if cb and cb.get("on_detections"):
                cb["on_detections"](payload)

        self.sio.connect(
            INFERENCE_WS_URL,
            transports=["websocket"]
        )

    def subscribe(self, run_id: str, on_frame, on_detections):
        run_id = str(run_id)
        with self._lock:
            self._callbacks[run_id] = {
                "on_frame": on_frame,
                "on_detections": on_detections
            }

        self.sio.emit("infer_subscribe", {"run_id": run_id})

    def unsubscribe(self, run_id: str):
        run_id = str(run_id)
        try:
            self.sio.emit("infer_unsubscribe", {"run_id": run_id})
        finally:
            with self._lock:
                self._callbacks.pop(run_id, None)


# singleton
inference_client = InferenceSocketClient()
