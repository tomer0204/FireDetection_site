from app import db
from .timestamps import TimestampedModel

class Track(TimestampedModel):
    __tablename__ = "tracks"

    track_id = db.Column(db.Integer, primary_key=True)

    camera_id = db.Column(
        db.Integer,
        db.ForeignKey("cameras.camera_id"),
        nullable=False
    )

    detections = db.relationship("Detection", backref="track", lazy=True)
