"""
Main application module for Config API.

This module contains the Flask application factory and setup logic.
"""

from flask import Flask, jsonify
from .config import Config
from .api import api_bp
from .exceptions import AuthenticationError, InvalidAPIKeyError, KeyNotValidatedError


def create_app(config_class=Config):
    """Create and configure an instance of the Flask application.

    Args:
        config_class: Configuration class to use for the application.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    # Health check endpoint
    @app.route("/health")
    def health():
        return {"status": "healthy", "service": "config-api"}

    # Error handlers for authentication exceptions
    @app.errorhandler(AuthenticationError)
    def handle_auth_error(error):
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 401

    @app.errorhandler(InvalidAPIKeyError)
    def handle_invalid_key_error(error):
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 403

    @app.errorhandler(KeyNotValidatedError)
    def handle_key_not_validated_error(error):
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 403

    return app
