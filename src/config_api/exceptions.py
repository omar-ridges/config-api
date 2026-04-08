"""
Custom exceptions module for Config API.

This module defines all custom exceptions used throughout the application.
"""


class ConfigAPIError(Exception):
    """Base exception for Config API errors."""

    def __init__(self, message: str = None):
        self.message = message or "An error occurred in Config API"
        super().__init__(self.message)


class ConfigNotFoundError(ConfigAPIError):
    """Raised when a requested configuration is not found."""

    def __init__(self, message: str = "Configuration not found"):
        super().__init__(message)


class ConfigValidationError(ConfigAPIError):
    """Raised when configuration data fails validation."""

    def __init__(self, message: str = "Configuration validation failed"):
        super().__init__(message)


class ConfigStorageError(ConfigAPIError):
    """Raised when there is an error with configuration storage."""

    def __init__(self, message: str = "Configuration storage error"):
        super().__init__(message)


class AuthenticationError(ConfigAPIError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message)


class InvalidAPIKeyError(AuthenticationError):
    """Raised when an invalid API key is provided."""

    def __init__(self, message: str = "Invalid API key"):
        super().__init__(message)


class KeyNotValidatedError(AuthenticationError):
    """Raised when API key is valid but not validated (no credit card on file)."""

    def __init__(self, message: str = "API key not validated - credit card required"):
        super().__init__(message)
