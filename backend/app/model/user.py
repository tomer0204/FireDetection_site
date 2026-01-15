from app.extensions import db
from .timestamps import TimestampedModel
import enum

class UserRole(enum.Enum):
    viewer = "viewer"
    admin = "admin"

class User(TimestampedModel):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)

    role = db.Column(
        db.Enum(UserRole, name="user_role"),
        nullable=False,
        default=UserRole.viewer
    )

    is_active = db.Column(db.Boolean, nullable=False, default=True)
