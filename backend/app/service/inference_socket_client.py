import threading
import socketio

class InferenceSocketClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.sio = socketio.Client(reconnection=True, reconnection_attempts=9999, reconnection_delay=1)
        self._lock = threading.Lock()
        self._connected = False

        @self.sio.event
        def connect():
            with self._lock:
                self._connected = True

        @self.sio.event
        def disconnect():
            with self._lock:
                self._connected = False

    def ensure_connected(self):
        with self._lock:
            connected = self._connected
        if connected:
            return

        self.sio.connect(self.base_url, transports=["websocket"], wait=True, wait_timeout=10)

    def subscribe(self, run_id: str):
        self.ensure_connected()
        self.sio.emit("infer_subscribe", {"run_id": run_id})

    def unsubscribe(self, run_id: str):
        try:
            self.sio.emit("infer_unsubscribe", {"run_id": run_id})
        except Exception:
            pass

    def on_frame(self, handler):
        self.sio.on("infer_frame", handler)

    def disconnect_client(self):
        try:
            self.sio.disconnect()
        except Exception:
            pass
