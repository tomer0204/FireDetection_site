from app.extensions import db
from app.model.camera import Camera

def list_cameras():
    return Camera.query.order_by(Camera.camera_id.asc()).all()

def get_camera_by_id(camera_id: int):
    return Camera.query.get(camera_id)

def create_camera(name: str, lat: float, lng: float):
    camera = Camera(name=name, lat=lat, lng=lng)
    db.session.add(camera)
    db.session.commit()
    return camera
