"""
Entry point for running Config API as a module.

Usage:
    python -m config_api
"""

from .app import create_app
from .config import DevelopmentConfig


def main():
    """Run the Config API application."""
    app = create_app(DevelopmentConfig)
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()