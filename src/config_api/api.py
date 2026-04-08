"""
API routes module for Config API.

This module contains all API endpoints for configuration management.
"""

from flask import Blueprint, current_app, jsonify, request
from .models import ConfigManager
from .auth import APIKeyManager, require_auth
from .exceptions import ConfigNotFoundError, ConfigValidationError

api_bp = Blueprint("api", __name__)


def get_config_manager():
    """Get a ConfigManager instance with the current app config."""
    storage_path = current_app.config.get("CONFIG_STORAGE_PATH")
    return ConfigManager(storage_path=storage_path)


def get_key_manager():
    """Get an APIKeyManager instance with the current app config."""
    storage_path = current_app.config.get("KEY_STORAGE_PATH")
    return APIKeyManager(storage_path=storage_path)


@api_bp.route("/auth/key", methods=["POST"])
def request_api_key():
    """Request a new API key.

    Expects JSON body with 'email' field.
    Returns the generated API key.
    """
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "status": "error",
            "message": "Request body required"
        }), 400

    email = data.get("email")
    if not email:
        return jsonify({
            "status": "error",
            "message": "Email is required"
        }), 400

    try:
        key_manager = get_key_manager()
        key, validation_token = key_manager.generate_key(email)
        
        # Send credit card form email
        email_sent = key_manager.send_credit_card_form_email(email, key, validation_token)
        
        if email_sent:
            return jsonify({
                "status": "success",
                "data": {
                    "key": key,
                    "email": email,
                    "message": "Key generated. Credit card form has been sent to your email."
                }
            }), 201
        else:
            # If email fails, still return the key but warn the user
            return jsonify({
                "status": "success",
                "data": {
                    "key": key,
                    "email": email,
                    "message": "Key generated but failed to send email. Please contact support."
                }
            }), 201
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@api_bp.route("/auth/validate", methods=["GET", "POST"])
def validate_key_endpoint():
    """Validate an API key using a secure validation token.

    This endpoint validates the API key after credit card form submission.
    The validation token is sent via email and is required to activate the key.
    
    For GET requests: token is passed as query parameter.
    For POST requests: token is passed in form data or JSON body.
    """
    # Get token from query param, form data, or JSON body
    token = request.args.get('token')
    
    if not token and request.method == 'POST':
        if request.is_json:
            data = request.get_json(silent=True) or {}
            token = data.get('token')
        else:
            token = request.form.get('token')
    
    if not token:
        return jsonify({
            "status": "error",
            "message": "Validation token is required"
        }), 400

    key_manager = get_key_manager()
    
    # Validate using the secure token
    success = key_manager.validate_with_token(token)

    if success:
        return jsonify({
            "status": "success",
            "message": "API key validated successfully. Your key is now active and can be used to access the API."
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Invalid or expired validation token"
        }), 400


@api_bp.route("/auth/key", methods=["DELETE"])
@require_auth
def deregister_key():
    """Deregister (delete) an API key.

    The API key to deregister is provided in the X-API-Key header.
    
    Returns:
        JSON response with deregistration status.
    """
    key = request.headers.get('X-API-Key')
    
    key_manager = get_key_manager()
    success = key_manager.deregister_key(key)
    
    if success:
        return jsonify({
            "status": "success",
            "message": "API key deregistered successfully"
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Failed to deregister API key"
        }), 400


@api_bp.route("/auth/key/email", methods=["PUT"])
@require_auth
def update_key_email():
    """Update the email address associated with an API key.

    Expects JSON body with 'email' field.
    The API key to update is provided in the X-API-Key header.
    
    Returns:
        JSON response with update status.
    """
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "status": "error",
            "message": "Request body required"
        }), 400

    new_email = data.get("email")
    if not new_email:
        return jsonify({
            "status": "error",
            "message": "Email is required"
        }), 400

    key = request.headers.get('X-API-Key')
    key_manager = get_key_manager()
    
    success = key_manager.update_email(key, new_email)
    
    if success:
        return jsonify({
            "status": "success",
            "message": "Email address updated successfully",
            "data": {
                "email": new_email
            }
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Failed to update email address"
        }), 400


@api_bp.route("/configs", methods=["GET"])
@require_auth
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
@require_auth
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
@require_auth
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
@require_auth
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
@require_auth
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
