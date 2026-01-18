from app.schema.auth_schema import RegisterSchema, LoginSchema
from app.service.auth_service import register_user, login_user

def register(data: dict):
    payload = RegisterSchema(**data)
    user = register_user(payload.email, payload.username, payload.password)
    return user

def login(data: dict):
    payload = LoginSchema(**data)
    user, access_token, refresh_token = login_user(payload.username, payload.password)
    return user, access_token, refresh_token
