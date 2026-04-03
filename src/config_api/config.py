"""
Configuration module for Config API.

This module contains configuration classes for different environments.
"""

import os


class Config:
    """Base configuration class.

    Contains default configuration settings for the application.
    """

    # Flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    DEBUG = False
    TESTING = False

    # API settings
    API_TITLE = "Config API"
    API_VERSION = "v1"

    # Storage settings
    CONFIG_STORAGE_PATH = os.environ.get(
        "CONFIG_STORAGE_PATH",
        os.path.join(os.path.dirname(__file__), "..", "..", "data")
    )
    KEY_STORAGE_PATH = os.environ.get(
        "KEY_STORAGE_PATH",
        os.path.join(os.path.dirname(__file__), "..", "..", "keys")
    )

    # Email settings
    SMTP_HOST = os.environ.get("SMTP_HOST", "localhost")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.environ.get("SMTP_FROM_EMAIL", "noreply@configapi.com")
    API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:5000")


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG = True


class TestingConfig(Config):
    """Testing environment configuration."""

    TESTING = True
    DEBUG = True
    CONFIG_STORAGE_PATH = "/tmp/config-api-test"
    KEY_STORAGE_PATH = "/tmp/config-api-test-keys"


class ProductionConfig(Config):
    """Production environment configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY")

    @classmethod
    def init_app(cls, app):
        """Initialize production-specific settings."""
        assert cls.SECRET_KEY, "SECRET_KEY must be set in production"
