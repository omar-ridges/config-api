"""
API routes module for Config API.

This module contains all API endpoints for configuration management.
"""

from flask import Blueprint, current_app, jsonify, request
from .models import ConfigManager
from .exceptions import ConfigNotFoundError, ConfigValidationError

api_bp = Blueprint("api", __name__)


def get_config_manager():
    """Get a ConfigManager instance with the current app config."""
    storage_path = current_app.config.get("CONFIG_STORAGE_PATH")
    return ConfigManager(storage_path=storage_path)


@api_bp.route("/configs", methods=["GET"])
def list_configs():
    """List all available configuration files.

    Returns:
        JSON response with list of configuration names.
    """
    configs = get_config_manager().list_configs()
    return jsonify({
        "status": "success",
        "data": configs
    })


@api_bp.route("/configs/<name>", methods=["GET"])
def get_config(name):
    """Get a specific configuration by name.

    Args:
        name: Name of the configuration file.

    Returns:
        JSON response with configuration content.
    """
    try:
        config = get_config_manager().get_config(name)
        return jsonify({
            "status": "success",
            "data": config
        })
    except ConfigNotFoundError:
        return jsonify({
            "status": "error",
            "message": f"Configuration '{name}' not found"
        }), 404


@api_bp.route("/configs/<name>", methods=["POST"])
def create_config(name):
    """Create a new configuration file.

    Args:
        name: Name of the configuration file.

    Returns:
        JSON response with creation status.
    """
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "status": "error",
            "message": "No configuration data provided"
        }), 400

    try:
        get_config_manager().create_config(name, data)
        return jsonify({
            "status": "success",
            "message": f"Configuration '{name}' created successfully"
        }), 201
    except ConfigValidationError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@api_bp.route("/configs/<name>", methods=["PUT"])
def update_config(name):
    """Update an existing configuration file.

    Args:
        name: Name of the configuration file.

    Returns:
        JSON response with update status.
    """
    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "No configuration data provided"
        }), 400

    try:
        get_config_manager().update_config(name, data)
        return jsonify({
            "status": "success",
            "message": f"Configuration '{name}' updated successfully"
        })
    except ConfigNotFoundError:
        return jsonify({
            "status": "error",
            "message": f"Configuration '{name}' not found"
        }), 404
    except ConfigValidationError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@api_bp.route("/configs/<name>", methods=["DELETE"])
def delete_config(name):
    """Delete a configuration file.

    Args:
        name: Name of the configuration file.

    Returns:
        JSON response with deletion status.
    """
    try:
        get_config_manager().delete_config(name)
        return jsonify({
            "status": "success",
            "message": f"Configuration '{name}' deleted successfully"
        })
    except ConfigNotFoundError:
        return jsonify({
            "status": "error",
            "message": f"Configuration '{name}' not found"
        }), 404
