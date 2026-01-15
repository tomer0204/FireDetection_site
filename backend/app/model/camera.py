from app.extensions import db

class Camera(db.Model):
    __tablename__ = "cameras"

    camera_id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

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
