from flask import Flask, request
from flask_cors import CORS
from app.config import DevelopmentConfig, ProductionConfig
from app.extensions import db, migrate, jwt, limiter

def create_app():
    app = Flask(__name__)

    import os
    app_env = os.getenv("APP_ENV", "development")

    if app_env == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)


    CORS(
        app,
        origins=app.config["CORS_ORIGINS"],
        supports_credentials=True,
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-CSRF-TOKEN"
        ],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = app.make_response("")
            response.status_code = 200
            return response

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)

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

    from app import model

    return app
