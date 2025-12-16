from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from backend.config import config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from .routes.user_routes import user_bp
    app.register_blueprint(user_bp)

    return app
