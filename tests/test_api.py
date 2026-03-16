"""
Tests for the API routes module.

This module contains integration tests for API endpoints.
"""

import json
import os
import tempfile
import unittest

from config_api import create_app
from config_api.config import TestingConfig


class TestAPI(unittest.TestCase):
    """Test cases for API endpoints."""

    def setUp(self):
        """Set up test fixtures before each test."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a fresh config class for each test to avoid shared state
        class FreshTestingConfig(TestingConfig):
            CONFIG_STORAGE_PATH = self.temp_dir
        
        self.app = create_app(FreshTestingConfig)
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up test fixtures after each test."""
        for filename in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, filename))
        os.rmdir(self.temp_dir)

    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "config-api")

    def test_list_configs_empty(self):
        """Test listing configs when empty."""
        response = self.client.get("/api/v1/configs")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"], [])

    def test_create_config(self):
        """Test creating a configuration."""
        config_data = {"key": "value", "number": 42}
        response = self.client.post(
            "/api/v1/configs/test-config",
            data=json.dumps(config_data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")

    def test_create_config_no_data(self):
        """Test creating a config without data."""
        response = self.client.post(
            "/api/v1/configs/test-config",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertEqual(data["status"], "error")

    def test_get_config(self):
        """Test getting a configuration."""
        # Create a config first
        config_data = {"test": "data"}
        self.client.post(
            "/api/v1/configs/my-config",
            data=json.dumps(config_data),
            content_type="application/json"
        )

        # Get it
        response = self.client.get("/api/v1/configs/my-config")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"], config_data)

    def test_get_config_not_found(self):
        """Test getting a non-existent configuration."""
        response = self.client.get("/api/v1/configs/non-existent")
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data)
        self.assertEqual(data["status"], "error")

    def test_update_config(self):
        """Test updating a configuration."""
        # Create a config first
        self.client.post(
            "/api/v1/configs/update-test",
            data=json.dumps({"old": "data"}),
            content_type="application/json"
        )

        # Update it
        new_data = {"new": "data"}
        response = self.client.put(
            "/api/v1/configs/update-test",
            data=json.dumps(new_data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")

    def test_update_config_not_found(self):
        """Test updating a non-existent configuration."""
        response = self.client.put(
            "/api/v1/configs/non-existent",
            data=json.dumps({"data": "value"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_config(self):
        """Test deleting a configuration."""
        # Create a config first
        self.client.post(
            "/api/v1/configs/delete-me",
            data=json.dumps({"data": "value"}),
            content_type="application/json"
        )

        # Delete it
        response = self.client.delete("/api/v1/configs/delete-me")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")

    def test_delete_config_not_found(self):
        """Test deleting a non-existent configuration."""
        response = self.client.delete("/api/v1/configs/non-existent")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
