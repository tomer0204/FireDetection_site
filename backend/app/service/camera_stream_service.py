from datetime import datetime
import os
import requests
from app.extensions import db
from app.model.camera import Camera
from app.model.camera_stream import CameraStream

ORCHESTRATOR_URL = os.getenv("INFERENCE_URL", "http://orchestrator:5001").rstrip("/")

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
    camera = Camera.query.get_or_404(int(camera_id))

    res = requests.post(
        f"{ORCHESTRATOR_URL}/streams/start",
        json={"camera_id": int(camera.camera_id), "fps": int(fps)},
        timeout=10
    )
    res.raise_for_status()
    data = res.json()

    stream = CameraStream(
        camera_id=int(camera_id),
        run_id=data["run_id"],
        source_type="VIDEO",
        source_ref=f"cam_{camera_id}",
        fps=int(fps),
        s3_prefix=data.get("s3_prefix"),
        started_at=datetime.utcnow(),
        is_active=True
    )

    db.session.add(stream)
    db.session.commit()
    return stream

def stop_stream(stream_id: int):
    stream = get_stream(int(stream_id))
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
