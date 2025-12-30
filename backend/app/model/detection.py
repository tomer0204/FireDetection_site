from app import db
from .timestamps import TimestampedModel

class Detection(TimestampedModel):
    __tablename__ = "detections"

    detection_id = db.Column(db.Integer, primary_key=True)

    camera_id = db.Column(
        db.Integer,
        db.ForeignKey("cameras.camera_id"),
        nullable=False
    )

    track_id = db.Column(
        db.Integer,
        db.ForeignKey("tracks.track_id"),
        nullable=False
    )

    coordinates = db.Column(db.JSON, nullable=False)
