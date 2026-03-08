import eventlet
eventlet.monkey_patch()

import os
import yaml
import boto3
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, join_room, leave_room

from core.stream_manager import StreamManager

CONFIG_PATH = os.getenv("CAMERAS_CONFIG", "configs/cameras.yaml")

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "fire-frames")

ENABLE_MINIO_ARCHIVE = os.getenv("ENABLE_MINIO_ARCHIVE", "true").lower() == "true"

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

def load_cameras():
    with open(CONFIG_PATH, "r") as f:
        data = yaml.safe_load(f) or {}
    cams = data.get("cameras", [])
    return {int(c["camera_id"]): c for c in cams}

class S3Writer:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=MINIO_ENDPOINT,
            aws_access_key_id=MINIO_ACCESS_KEY,
            aws_secret_access_key=MINIO_SECRET_KEY,
            region_name="us-east-1"
        )

    def ensure_bucket(self):
        buckets = [b["Name"] for b in self.s3.list_buckets().get("Buckets", [])]
        if MINIO_BUCKET not in buckets:
            self.s3.create_bucket(Bucket=MINIO_BUCKET)

    def put_jpeg(self, key: str, data: bytes):
        self.s3.put_object(
            Bucket=MINIO_BUCKET,
            Key=key,
            Body=data,
            ContentType="image/jpeg",
            CacheControl="no-store"
        )

cameras = load_cameras()
writer = S3Writer() if ENABLE_MINIO_ARCHIVE else None

manager = StreamManager(
    cameras=cameras,
    socketio=socketio,
    archive_writer=writer,
    enable_archive=ENABLE_MINIO_ARCHIVE
)

@app.get("/health")
def health():
    return jsonify({"ok": True, "state": manager.get_state()})

@app.post("/streams/start")
def http_start():
    data = request.get_json() or {}
    camera_id = int(data["camera_id"])
    fps = int(data.get("fps", 17))
    return jsonify(manager.start(camera_id, fps)), 200

@app.post("/streams/stop")
def http_stop():
    data = request.get_json() or {}
    manager.stop(data.get("run_id"))
    return jsonify({"stopped": True}), 200

@socketio.on("infer_subscribe")
def infer_subscribe(data):
    run_id = str(data["run_id"])
    join_room(f"run:{run_id}")
    socketio.emit("infer_subscribed", {"run_id": run_id})

@socketio.on("infer_unsubscribe")
def infer_unsubscribe(data):
    run_id = str(data["run_id"])
    leave_room(f"run:{run_id}")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5001)
