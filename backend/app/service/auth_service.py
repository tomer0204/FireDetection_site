from app.extensions import db
from app.model.user import User
from app.utils.security import hash_password, verify_password
from app.utils.errors import Conflict, Unauthorized, Forbidden
from flask_jwt_extended import create_access_token, create_refresh_token

def register_user(email, password, role="user"):
    existing = User.query.filter_by(email=email).first()
    if existing:
        raise Conflict("Email already in use")

    user = User(email=email, password=hash_password(password), role=role, is_active=True)
    db.session.add(user)
    db.session.commit()
    return user

def login_user(email, password):
    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(password, user.password):
        raise Unauthorized("Invalid credentials")

    if not user.is_active:
        raise Forbidden("User is inactive")

    access_token = create_access_token(identity=user.user_id, additional_claims={"role": user.role})
    refresh_token = create_refresh_token(identity=user.user_id)
    return user, access_token, refresh_token

def get_user_by_id(user_id):
    return User.query.get(user_id)
