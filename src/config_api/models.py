"""
Models module for Config API.

This module contains data models and business logic for configuration management.
"""

import json
import os
from typing import Any, Dict, List

from .config import Config
from .exceptions import ConfigNotFoundError, ConfigValidationError


class ConfigManager:
    """Manager class for configuration operations.

    Handles CRUD operations for configuration files with proper
    validation and error handling.
    """

    def __init__(self, storage_path: str = None):
        """Initialize the ConfigManager.

        Args:
            storage_path: Path to store configuration files.
                         Defaults to Config.CONFIG_STORAGE_PATH.
        """
        self.storage_path = storage_path or Config.CONFIG_STORAGE_PATH
        self._ensure_storage_exists()

    def _ensure_storage_exists(self) -> None:
        """Create storage directory if it does not exist."""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path, exist_ok=True)

    def _get_config_path(self, name: str) -> str:
        """Get the full path for a configuration file.

        Args:
            name: Name of the configuration.

        Returns:
            Full file path for the configuration.
        """
        return os.path.join(self.storage_path, f"{name}.json")

    def _validate_config_name(self, name: str) -> None:
        """Validate configuration name.

        Args:
            name: Name to validate.

        Raises:
            ConfigValidationError: If name is invalid.
        """
        if not name:
            raise ConfigValidationError("Configuration name cannot be empty")

        if "/" in name or "\\" in name:
            raise ConfigValidationError(
                "Configuration name cannot contain path separators"
            )

        if name.startswith("."):
            raise ConfigValidationError(
                "Configuration name cannot start with a dot"
            )

    def _validate_config_data(self, data: Dict[str, Any]) -> None:
        """Validate configuration data.

        Args:
            data: Configuration data to validate.

        Raises:
            ConfigValidationError: If data is invalid.
        """
        if not isinstance(data, dict):
            raise ConfigValidationError("Configuration data must be a JSON object")

    def list_configs(self) -> List[str]:
        """List all available configuration names.

        Returns:
            List of configuration names (without .json extension).
        """
        self._ensure_storage_exists()

        configs = []
        for filename in os.listdir(self.storage_path):
            if filename.endswith(".json"):
                configs.append(filename[:-5])  # Remove .json extension

        return sorted(configs)

    def get_config(self, name: str) -> Dict[str, Any]:
        """Get a configuration by name.

        Args:
            name: Name of the configuration.

        Returns:
            Configuration data as a dictionary.

        Raises:
            ConfigNotFoundError: If configuration does not exist.
        """
        self._validate_config_name(name)

        config_path = self._get_config_path(name)

        if not os.path.exists(config_path):
            raise ConfigNotFoundError(f"Configuration '{name}' not found")

        with open(config_path, "r") as f:
            return json.load(f)

    def create_config(self, name: str, data: Dict[str, Any]) -> None:
        """Create a new configuration.

        Args:
            name: Name of the configuration.
            data: Configuration data.

        Raises:
            ConfigValidationError: If name or data is invalid.
        """
        self._validate_config_name(name)
        self._validate_config_data(data)

        config_path = self._get_config_path(name)

        if os.path.exists(config_path):
            raise ConfigValidationError(
                f"Configuration '{name}' already exists"
            )

        with open(config_path, "w") as f:
            json.dump(data, f, indent=2)

    def update_config(self, name: str, data: Dict[str, Any]) -> None:
        """Update an existing configuration.

        Args:
            name: Name of the configuration.
            data: New configuration data.

        Raises:
            ConfigNotFoundError: If configuration does not exist.
            ConfigValidationError: If name or data is invalid.
        """
        self._validate_config_name(name)
        self._validate_config_data(data)

        config_path = self._get_config_path(name)

        if not os.path.exists(config_path):
            raise ConfigNotFoundError(f"Configuration '{name}' not found")

        with open(config_path, "w") as f:
            json.dump(data, f, indent=2)

    def delete_config(self, name: str) -> None:
        """Delete a configuration.

        Args:
            name: Name of the configuration.

        Raises:
            ConfigNotFoundError: If configuration does not exist.
        """
        self._validate_config_name(name)

        config_path = self._get_config_path(name)

        if not os.path.exists(config_path):
            raise ConfigNotFoundError(f"Configuration '{name}' not found")

        os.remove(config_path)
