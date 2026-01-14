from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config


db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    from app.route.user_routes import user_bp
    app.register_blueprint(user_bp, url_prefix="/api/users")
    return app

from app.model.user import User
from app.model.camera import Camera
from app.model.track import Track
from app.model.detection import Detection
