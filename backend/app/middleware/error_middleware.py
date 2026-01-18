from flask import jsonify, current_app
from sqlalchemy.exc import IntegrityError
import traceback

def register_error_handlers(app):

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(e):
        return jsonify({
            "error": "CONFLICT",
            "message": "Database constraint error"
        }), 409

    @app.errorhandler(Exception)
    def handle_generic_error(e):
        if current_app.config.get("DEBUG"):
            traceback.print_exc()
            return jsonify({
                "error": "INTERNAL_ERROR",
                "message": str(e)
            }), 500

        return jsonify({
            "error": "INTERNAL_ERROR",
            "message": "Something went wrong"
        }), 500
