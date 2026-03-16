"""
Main application module for Config API.

This module contains the Flask application factory and setup logic.
"""

from flask import Flask
from .config import Config
from .api import api_bp


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

    return app
