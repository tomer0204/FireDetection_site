from datetime import datetime
import time
import os
import requests
import boto3
from app.extensions import db
from app.model.camera import Camera
from app.model.camera_stream import CameraStream

ORCHESTRATOR_URL = os.getenv("INFERENCE_URL", "http://orchestrator:5001").rstrip("/")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
BUCKET = os.getenv("MINIO_BUCKET", "fire-frames")

s3 = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    region_name="us-east-1"
)



def get_stream(stream_id: int):
    return CameraStream.query.get(stream_id)

def get_active_streams_for_camera(camera_id: int):
    return (
        CameraStream.query
        .filter_by(camera_id=camera_id, is_active=True)
        .order_by(CameraStream.started_at.desc())
        .all()
    )


def create_stream(camera_id: int, fps: int):
    camera = Camera.query.get_or_404(camera_id)

    res = requests.post(
        f"{ORCHESTRATOR_URL}/streams/start",
        json={"camera_id": camera.camera_id, "fps": fps},
        timeout=10
    )
    res.raise_for_status()
    data = res.json()

    stream = CameraStream(
        camera_id=camera_id,
        run_id=data["run_id"],
        source_type="VIDEO",
        source_ref=f"cam_{camera_id}",
        fps=fps,
        s3_prefix=data["s3_prefix"],
        started_at=datetime.utcnow(),
        is_active=True
    )

    db.session.add(stream)
    db.session.commit()
    return stream

def stop_stream(stream_id: int):
    stream = get_stream(stream_id)
    if not stream or not stream.is_active:
        return None

    try:
        requests.post(
            f"{ORCHESTRATOR_URL}/streams/stop",
            json={"run_id": stream.run_id},
            timeout=5
        )
    except Exception:
        pass

    stream.is_active = False
    stream.ended_at = datetime.utcnow()
    db.session.commit()
    return stream

def get_latest_frame_by_prefix(s3_prefix: str):
    objs = s3.list_objects_v2(
        Bucket=BUCKET,
        Prefix=s3_prefix
    )

    if "Contents" not in objs or not objs["Contents"]:
        return None

    latest = max(objs["Contents"], key=lambda x: x["LastModified"])
    obj = s3.get_object(Bucket=BUCKET, Key=latest["Key"])
    return obj["Body"].read()


def live_frame_generator(stream: CameraStream, fps: int = 10):
    s3_prefix = stream.s3_prefix

    while True:
        frame = get_latest_frame_by_prefix(s3_prefix)
        if frame:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                frame +
                b"\r\n"
            )

        time.sleep(1.0 / fps)
