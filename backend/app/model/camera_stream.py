from app.extensions import db

class CameraStream(db.Model):
    __tablename__ = "camera_streams"

    stream_id = db.Column(db.Integer, primary_key=True)

    camera_id = db.Column(
        db.Integer,
        db.ForeignKey("cameras.camera_id"),
        nullable=False
    )

    run_id = db.Column(db.String(64), nullable=False)

    source_type = db.Column(db.String(32), nullable=False)
    source_ref = db.Column(db.String(255), nullable=False)

    fps = db.Column(db.Integer, nullable=False)

    s3_prefix = db.Column(db.String(255), nullable=False)

    started_at = db.Column(db.DateTime, nullable=False)
    ended_at = db.Column(db.DateTime, nullable=True)

    is_active = db.Column(db.Boolean, nullable=False, default=True)
