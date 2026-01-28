from flask_jwt_extended import create_access_token, create_refresh_token
from app.extensions import db
from app.model.user import User, UserRole
from app.security.password import hash_password, verify_password
from app.utils.errors import Unauthorized, Conflict, Forbidden

def register_user(email: str, username: str, password: str):
    if User.query.filter_by(email=email).first():
        raise Conflict("Email already exists")

    if User.query.filter_by(username=username).first():
        raise Conflict("Username already exists")

    user = User(
        email=email,
        username=username,
        password_hash=hash_password(password),
        role=UserRole.viewer
    )

    db.session.add(user)
    db.session.commit()
    return user

def login_user(username: str, password: str):
    user = User.query.filter_by(username=username).first()

    if not user:
        raise Unauthorized("Invalid username")

    if not verify_password(password, user.password_hash):
        raise Unauthorized("Invalid password")

    if not user.is_active:
        raise Forbidden("User is inactive")

    access_token = create_access_token(
        identity=str(user.user_id),
        additional_claims={"role": user.role.value}
    )

    refresh_token = create_refresh_token(identity=str(user.user_id))
    return user, access_token, refresh_token
