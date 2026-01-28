from app.extensions import db

class Camera(db.Model):
    __tablename__ = "cameras"

    camera_id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    is_enabled = db.Column(db.Boolean, nullable=False, default=True)

    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)

    tracks = db.relationship(
        "Track",
        backref="camera",
        cascade="all, delete-orphan",
        lazy=True
    )

    detections = db.relationship(
        "Detection",
        backref="camera",
        cascade="all, delete-orphan",
        lazy=True
    )

    streams = db.relationship(
        "CameraStream",
        backref="camera",
        cascade="all, delete-orphan",
        lazy=True
    )
