from flask import Flask, request
from flask_cors import CORS
from app.config import DevelopmentConfig, ProductionConfig
from app.extensions import db, migrate, jwt, limiter, socketio

def create_app():
    app = Flask(__name__)

    import os
    app_env = os.getenv("APP_ENV", "development")

    if app_env == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)

    socketio.init_app(
        app,
        cors_allowed_origins=app.config["CORS_ORIGINS"],
        async_mode="eventlet",
        ping_interval=20,
        ping_timeout=60
    )

    CORS(
        app,
        origins=app.config["CORS_ORIGINS"],
        supports_credentials=True,
    )
    from app.middleware.error_middleware import register_error_handlers
    register_error_handlers(app)

    from app.route.auth_routes import auth_bp
    from app.route.camera_routes import camera_bp
    from app.route.camera_stream_routes import stream_bp
    from app.route.health_routes import health_bp
    from app.route.favicon_route import favicon_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(camera_bp, url_prefix="/api")
    app.register_blueprint(stream_bp, url_prefix="/api")
    app.register_blueprint(health_bp)
    app.register_blueprint(favicon_bp)

    from app.utils.stream_socket import register_stream_ws
    register_stream_ws(app)

    from app import model

    return app
