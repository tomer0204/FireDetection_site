import uuid
from sqlalchemy.dialects.postgresql import UUID
from backend.app import db
from .timestamps import TimestampedModel

class User(TimestampedModel):
    __tablename__ = "users"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


    cameras = db.relationship("Camera", back_populates="owner")
