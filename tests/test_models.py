"""
Tests for the models module.

This module contains unit tests for ConfigManager and related classes.
"""

import json
import os
import tempfile
import unittest

from config_api.models import ConfigManager
from config_api.exceptions import ConfigNotFoundError, ConfigValidationError


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager class."""

    def setUp(self):
        """Set up test fixtures before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ConfigManager(storage_path=self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures after each test."""
        # Remove all files in temp directory
        for filename in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, filename))
        os.rmdir(self.temp_dir)

    def test_list_configs_empty(self):
        """Test listing configs when storage is empty."""
        configs = self.manager.list_configs()
        self.assertEqual(configs, [])

    def test_create_config(self):
        """Test creating a new configuration."""
        data = {"key": "value", "nested": {"inner": "data"}}
        self.manager.create_config("test-config", data)

        # Verify file was created
        config_path = os.path.join(self.temp_dir, "test-config.json")
        self.assertTrue(os.path.exists(config_path))

        # Verify content
        with open(config_path, "r") as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data, data)

    def test_get_config(self):
        """Test retrieving a configuration."""
        data = {"test": "data"}
        self.manager.create_config("my-config", data)

        result = self.manager.get_config("my-config")
        self.assertEqual(result, data)

    def test_get_config_not_found(self):
        """Test retrieving a non-existent configuration."""
        with self.assertRaises(ConfigNotFoundError):
            self.manager.get_config("non-existent")

    def test_update_config(self):
        """Test updating an existing configuration."""
        # Create initial config
        self.manager.create_config("update-test", {"old": "data"})

        # Update it
        new_data = {"new": "data", "added": "field"}
        self.manager.update_config("update-test", new_data)

        # Verify update
        result = self.manager.get_config("update-test")
        self.assertEqual(result, new_data)

    def test_update_config_not_found(self):
        """Test updating a non-existent configuration."""
        with self.assertRaises(ConfigNotFoundError):
            self.manager.update_config("non-existent", {"data": "value"})

    def test_delete_config(self):
        """Test deleting a configuration."""
        self.manager.create_config("delete-me", {"data": "value"})
        self.manager.delete_config("delete-me")

        # Verify file was deleted
        config_path = os.path.join(self.temp_dir, "delete-me.json")
        self.assertFalse(os.path.exists(config_path))

    def test_delete_config_not_found(self):
        """Test deleting a non-existent configuration."""
        with self.assertRaises(ConfigNotFoundError):
            self.manager.delete_config("non-existent")

    def test_validate_config_name_empty(self):
        """Test validation of empty config name."""
        with self.assertRaises(ConfigValidationError):
            self.manager._validate_config_name("")

    def test_validate_config_name_with_path_separator(self):
        """Test validation of config name with path separator."""
        with self.assertRaises(ConfigValidationError):
            self.manager._validate_config_name("config/name")

    def test_validate_config_name_starting_with_dot(self):
        """Test validation of config name starting with dot."""
        with self.assertRaises(ConfigValidationError):
            self.manager._validate_config_name(".hidden")

    def test_validate_config_data_not_dict(self):
        """Test validation of non-dict config data."""
        with self.assertRaises(ConfigValidationError):
            self.manager._validate_config_data("not a dict")

    def test_create_duplicate_config(self):
        """Test creating a config that already exists."""
        self.manager.create_config("duplicate", {"data": "value"})

        with self.assertRaises(ConfigValidationError):
            self.manager.create_config("duplicate", {"data": "other"})


if __name__ == "__main__":
    unittest.main()
