from datetime import datetime
import time
import uuid
import requests
import boto3
from app.extensions import db
from app.model.camera_stream import CameraStream

INFERENCE_URL = "http://localhost:8081"
BUCKET = "fire-frames"

s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadmin",
    region_name="us-east-1"
)

def get_active_stream(camera_id: int):
    return (
        CameraStream.query
        .filter_by(camera_id=camera_id, is_active=True)
        .order_by(CameraStream.started_at.desc())
        .first()
    )

def start_camera_stream(camera_id: int, source_ref: str, fps: int):
    local_run_id = uuid.uuid4().hex

    res = requests.post(
        f"{INFERENCE_URL}/streams/start",
        json={
            "camera_id": camera_id,
            "source_ref": source_ref,
            "fps": fps
        },
        timeout=10
    )
    res.raise_for_status()
    data = res.json() if res.content else {}

    run_id = data.get("run_id", local_run_id)
    s3_prefix = data.get("s3_prefix", f"{camera_id}/{run_id}/")

    stream = CameraStream(
        camera_id=camera_id,
        run_id=run_id,
        source_type="MINIO",
        source_ref=source_ref,
        fps=fps,
        s3_prefix=s3_prefix,
        started_at=datetime.utcnow(),
        ended_at=None,
        is_active=True
    )

    db.session.add(stream)
    db.session.commit()
    return stream

def stop_camera_stream(camera_id: int):
    stream = get_active_stream(camera_id)
    if not stream:
        return None

    try:
        requests.post(
            f"{INFERENCE_URL}/streams/stop",
            json={"camera_id": camera_id, "run_id": stream.run_id},
            timeout=10
        )
    except Exception:
        pass

    stream.is_active = False
    stream.ended_at = datetime.utcnow()
    db.session.commit()
    return stream

def get_latest_frame_bytes(camera_id: int):
    stream = get_active_stream(camera_id)
    if not stream:
        return None

    objs = s3.list_objects_v2(Bucket=BUCKET, Prefix=stream.s3_prefix)
    if "Contents" not in objs or not objs["Contents"]:
        return None

    latest = max(objs["Contents"], key=lambda x: x["Key"])
    obj = s3.get_object(Bucket=BUCKET, Key=latest["Key"])
    return obj["Body"].read()

def live_frame_generator(camera_id: int, fps: int = 17):
    while True:
        frame = get_latest_frame_bytes(camera_id)
        if frame:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                frame +
                b"\r\n"
            )
        time.sleep(1.0 / max(1, fps))
