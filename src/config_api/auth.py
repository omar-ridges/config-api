import json
import logging
import os
import secrets
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps
from flask import request, jsonify, current_app
from .exceptions import AuthenticationError, InvalidAPIKeyError, KeyNotValidatedError


class APIKeyManager:
    """Manager class for API key operations.

    Handles key generation, storage, validation, and credit card association.
    """

    def __init__(self, storage_path: str = None):
        """Initialize the APIKeyManager.

        Args:
            storage_path: Path to store API key data.
        """
        self.storage_path = storage_path or "./keys"
        self._ensure_storage_exists()
        self.keys_file = os.path.join(self.storage_path, "api_keys.json")

    def _ensure_storage_exists(self) -> None:
        """Create storage directory if it does not exist."""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path, exist_ok=True)

    def _load_keys(self) -> dict:
        """Load API keys from storage.

        Returns:
            Dictionary of API keys.
        """
        if not os.path.exists(self.keys_file):
            return {}
        
        with open(self.keys_file, "r") as f:
            return json.load(f)

    def _save_keys(self, keys: dict) -> None:
        """Save API keys to storage.

        Args:
            keys: Dictionary of API keys to save.
        """
        with open(self.keys_file, "w") as f:
            json.dump(keys, f, indent=2)

    def generate_key(self, email: str) -> tuple:
        """Generate a new API key for the given email.

        Args:
            email: Email address associated with the key request.

        Returns:
            Tuple of (API key string, validation token).
        """
        if not email:
            raise ValueError("Email is required")

        # Generate a secure random key and validation token
        key = secrets.token_urlsafe(32)
        validation_token = secrets.token_urlsafe(32)
        
        # Load existing keys
        keys = self._load_keys()
        
        # Store key with email and default values
        keys[key] = {
            "email": email,
            "credit_card_on_file": False,
            "validation_token": validation_token,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Save updated keys
        self._save_keys(keys)
        
        return key, validation_token

    def validate_key(self, key: str) -> bool:
        """Validate if an API key is valid and has credit card on file.

        Args:
            key: API key to validate.

        Returns:
            True if key is valid and has credit card on file, False otherwise.
        """
        if not key:
            return False
            
        keys = self._load_keys()
        key_data = keys.get(key)
        
        if not key_data:
            return False
            
        return key_data.get("credit_card_on_file", False)

    def get_key_data(self, key: str) -> dict:
        """Get data associated with an API key.

        Args:
            key: API key to look up.

        Returns:
            Dictionary with key data or None if not found.
        """
        if not key:
            return None
            
        keys = self._load_keys()
        return keys.get(key)

    def mark_credit_card_added(self, key: str) -> bool:
        """Mark that a credit card has been added for the given key.

        Args:
            key: API key to update.

        Returns:
            True if successfully updated, False if key not found.
        """
        if not key:
            return False
            
        keys = self._load_keys()
        key_data = keys.get(key)
        
        if not key_data:
            return False
            
        key_data["credit_card_on_file"] = True
        self._save_keys(keys)
        return True

    def validate_with_token(self, validation_token: str) -> bool:
        """Validate an API key using its validation token.

        This is a secure way to validate a key after credit card form submission.
        The validation token is sent via email and should only be known to the key owner.

        Args:
            validation_token: The validation token sent via email.

        Returns:
            True if validation successful, False otherwise.
        """
        if not validation_token:
            return False
            
        keys = self._load_keys()
        
        # Find the key with matching validation token
        for key, key_data in keys.items():
            if key_data.get("validation_token") == validation_token:
                # Mark credit card as added
                key_data["credit_card_on_file"] = True
                # Remove validation token after use (one-time use)
                del key_data["validation_token"]
                self._save_keys(keys)
                return True
                
        return False

    def send_credit_card_form_email(self, email: str, api_key: str, validation_token: str) -> bool:
        """Send credit card form email to the user.

        Args:
            email: Recipient email address.
            api_key: The API key for the user.
            validation_token: The validation token for secure validation.

        Returns:
            True if email sent successfully, False otherwise.
        """
        try:
            # Get email configuration from Flask app config
            smtp_host = current_app.config.get('SMTP_HOST', 'localhost')
            smtp_port = current_app.config.get('SMTP_PORT', 587)
            smtp_user = current_app.config.get('SMTP_USER', '')
            smtp_password = current_app.config.get('SMTP_PASSWORD', '')
            from_email = current_app.config.get('SMTP_FROM_EMAIL', 'noreply@configapi.com')
            api_base_url = current_app.config.get('API_BASE_URL', 'http://localhost:5000')
            
            # Create validation URL
            validation_url = f"{api_base_url}/api/v1/auth/validate?token={validation_token}"
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Complete Your API Key Registration - Credit Card Form'
            msg['From'] = from_email
            msg['To'] = email
            
            # Plain text version
            text_body = f"""
Thank you for requesting an API key.

Your API Key: {api_key}

To complete your registration and activate your API key, please submit your credit card information using the secure link below:

{validation_url}

This link is unique to your account and can only be used once.

If you did not request this API key, please ignore this email.
            """
            
            # HTML version with credit card form
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
        .content {{ background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
        .api-key {{ background-color: #e8f5e9; padding: 10px; border-left: 4px solid #4CAF50; margin: 15px 0; font-family: monospace; }}
        .button {{ display: inline-block; background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 15px 0; }}
        .footer {{ margin-top: 20px; font-size: 12px; color: #666; }}
        .warning {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Complete Your API Key Registration</h1>
        </div>
        <div class="content">
            <p>Thank you for requesting an API key. To activate your key and access the API, please complete the credit card form below.</p>
            
            <div class="api-key">
                <strong>Your API Key:</strong><br>
                {api_key}
            </div>
            
            <h3>Credit Card Information</h3>
            <form action="{validation_url}" method="POST" style="background: white; padding: 20px; border: 1px solid #ddd;">
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: bold;">Cardholder Name:</label>
                    <input type="text" name="cardholder_name" required style="width: 100%; padding: 8px; border: 1px solid #ddd; box-sizing: border-box;">
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: bold;">Card Number:</label>
                    <input type="text" name="card_number" placeholder="1234 5678 9012 3456" required style="width: 100%; padding: 8px; border: 1px solid #ddd; box-sizing: border-box;">
                </div>
                
                <div style="display: flex; gap: 15px; margin-bottom: 15px;">
                    <div style="flex: 1;">
                        <label style="display: block; margin-bottom: 5px; font-weight: bold;">Expiry Date:</label>
                        <input type="text" name="expiry_date" placeholder="MM/YY" required style="width: 100%; padding: 8px; border: 1px solid #ddd; box-sizing: border-box;">
                    </div>
                    <div style="flex: 1;">
                        <label style="display: block; margin-bottom: 5px; font-weight: bold;">CVV:</label>
                        <input type="text" name="cvv" placeholder="123" required style="width: 100%; padding: 8px; border: 1px solid #ddd; box-sizing: border-box;">
                    </div>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: bold;">Billing Address:</label>
                    <textarea name="billing_address" rows="3" required style="width: 100%; padding: 8px; border: 1px solid #ddd; box-sizing: border-box;"></textarea>
                </div>
                
                <button type="submit" style="background-color: #4CAF50; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px;">
                    Submit and Activate API Key
                </button>
            </form>
            
            <div class="warning">
                <strong>Security Notice:</strong> This validation link is unique to your account and can only be used once. Do not share this email with others.
            </div>
        </div>
        <div class="footer">
            <p>If you did not request this API key, please ignore this email.</p>
            <p>This is an automated message from Config API.</p>
        </div>
    </div>
</body>
</html>
            """
            
            # Attach parts
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                if smtp_user and smtp_password:
                    server.starttls()
                    server.login(smtp_user, smtp_password)
                server.sendmail(from_email, email, msg.as_string())
            
            return True
            
        except Exception as e:
            # Log the error
            logging.error(f"Failed to send email: {e}")
            return False

def require_auth(f):
    """Decorator to require API key authentication for endpoints.

    Checks for X-API-Key header and validates the key.
    Raises AuthenticationError subclasses for different failure cases.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Allow health check endpoint to be public
        if request.endpoint == 'health':
            return f(*args, **kwargs)
            
        key = request.headers.get('X-API-Key')
        if not key:
            raise AuthenticationError("API key required")
            
        # Initialize key manager with configured storage path
        storage_path = current_app.config.get('KEY_STORAGE_PATH')
        key_manager = APIKeyManager(storage_path=storage_path)
        
        # Check if key exists
        key_data = key_manager.get_key_data(key)
        if not key_data:
            raise InvalidAPIKeyError("Invalid API key")
            
        # Check if key has been validated (credit card on file)
        if not key_data.get("credit_card_on_file", False):
            raise KeyNotValidatedError("API key not validated - credit card required")
            
        return f(*args, **kwargs)
    return decorated_function
