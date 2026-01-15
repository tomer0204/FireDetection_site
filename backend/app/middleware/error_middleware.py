from flask import jsonify
from sqlalchemy.exc import IntegrityError
from app.utils.errors import AppError, BadRequest

def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(e):
        return jsonify({"error": e.code, "message": e.message}), e.status_code

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(e):
        return jsonify({"error": "CONFLICT", "message": "Database constraint error"}), 409

    @app.errorhandler(Exception)
    def handle_generic_error(e):
        return jsonify({"error": "INTERNAL_ERROR", "message": "Something went wrong"}), 500
