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


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG = True


class TestingConfig(Config):
    """Testing environment configuration."""

    TESTING = True
    DEBUG = True
    CONFIG_STORAGE_PATH = "/tmp/config-api-test"


class ProductionConfig(Config):
    """Production environment configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY")

    @classmethod
    def init_app(cls, app):
        """Initialize production-specific settings."""
        assert cls.SECRET_KEY, "SECRET_KEY must be set in production"
