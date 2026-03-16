#!/usr/bin/env python3
"""
Entry point for running the Config API application.

This script provides a convenient way to start the development server.
"""

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from config_api import create_app
from config_api.config import DevelopmentConfig


def main():
    """Run the Config API application."""
    app = create_app(DevelopmentConfig)
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()