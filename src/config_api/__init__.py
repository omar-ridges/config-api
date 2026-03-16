"""
Config API - An API for managing configuration files.

This package provides a RESTful API for storing, retrieving,
and managing configuration files from anywhere.

Example:
    >>> from config_api import create_app
    >>> app = create_app()
    >>> app.run()
"""

__version__ = "0.1.0"
__author__ = "Config API Team"

from .app import create_app
from .config import Config, DevelopmentConfig, ProductionConfig

__all__ = [
    "create_app",
    "Config",
    "DevelopmentConfig",
    "ProductionConfig",
]