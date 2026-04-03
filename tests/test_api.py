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
        self.key_temp_dir = tempfile.mkdtemp()
        
        # Create a fresh config class for each test to avoid shared state
        class FreshTestingConfig(TestingConfig):
            CONFIG_STORAGE_PATH = self.temp_dir
            KEY_STORAGE_PATH = self.key_temp_dir
        
        self.app = create_app(FreshTestingConfig)
        self.client = self.app.test_client()
        
        # Create a valid API key for testing
        self.api_key = self._create_valid_api_key()

    def tearDown(self):
        """Clean up test fixtures after each test."""
        for filename in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, filename))
        os.rmdir(self.temp_dir)
        
        for filename in os.listdir(self.key_temp_dir):
            os.remove(os.path.join(self.key_temp_dir, filename))
        os.rmdir(self.key_temp_dir)

    def _create_valid_api_key(self):
        """Create and validate a test API key."""
        # Request a key
        response = self.client.post(
            "/api/v1/auth/key",
            data=json.dumps({"email": "test@example.com"}),
            content_type="application/json"
        )
        data = json.loads(response.data)
        key = data["data"]["key"]
        
        # Get the validation token from the key data
        from config_api.auth import APIKeyManager
        key_manager = APIKeyManager(storage_path=self.key_temp_dir)
        key_data = key_manager.get_key_data(key)
        validation_token = key_data.get("validation_token")
        
        # Validate the key using the token
        self.client.get(f"/api/v1/auth/validate?token={validation_token}")
        
        return key

    def _auth_headers(self):
        """Return headers with valid API key."""
        return {"X-API-Key": self.api_key}

    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "config-api")

    def test_list_configs_empty(self):
        """Test listing configs when empty."""
        response = self.client.get("/api/v1/configs", headers=self._auth_headers())
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
            content_type="application/json",
            headers=self._auth_headers()
        )
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")

    def test_create_config_no_data(self):
        """Test creating a config without data."""
        response = self.client.post(
            "/api/v1/configs/test-config",
            content_type="application/json",
            headers=self._auth_headers()
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
            content_type="application/json",
            headers=self._auth_headers()
        )

        # Get it
        response = self.client.get("/api/v1/configs/my-config", headers=self._auth_headers())
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"], config_data)

    def test_get_config_not_found(self):
        """Test getting a non-existent configuration."""
        response = self.client.get("/api/v1/configs/non-existent", headers=self._auth_headers())
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data)
        self.assertEqual(data["status"], "error")

    def test_update_config(self):
        """Test updating a configuration."""
        # Create a config first
        self.client.post(
            "/api/v1/configs/update-test",
            data=json.dumps({"old": "data"}),
            content_type="application/json",
            headers=self._auth_headers()
        )

        # Update it
        new_data = {"new": "data"}
        response = self.client.put(
            "/api/v1/configs/update-test",
            data=json.dumps(new_data),
            content_type="application/json",
            headers=self._auth_headers()
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")

    def test_update_config_not_found(self):
        """Test updating a non-existent configuration."""
        response = self.client.put(
            "/api/v1/configs/non-existent",
            data=json.dumps({"data": "value"}),
            content_type="application/json",
            headers=self._auth_headers()
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_config(self):
        """Test deleting a configuration."""
        # Create a config first
        self.client.post(
            "/api/v1/configs/delete-me",
            data=json.dumps({"data": "value"}),
            content_type="application/json",
            headers=self._auth_headers()
        )

        # Delete it
        response = self.client.delete("/api/v1/configs/delete-me", headers=self._auth_headers())
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")

    def test_delete_config_not_found(self):
        """Test deleting a non-existent configuration."""
        response = self.client.delete("/api/v1/configs/non-existent", headers=self._auth_headers())
        self.assertEqual(response.status_code, 404)

    def test_auth_missing_key(self):
        """Test accessing protected endpoint without API key."""
        response = self.client.get("/api/v1/configs")
        self.assertEqual(response.status_code, 401)
        
        data = json.loads(response.data)
        self.assertEqual(data["status"], "error")
        self.assertEqual(data["message"], "API key required")

    def test_auth_invalid_key(self):
        """Test accessing protected endpoint with invalid API key."""
        response = self.client.get(
            "/api/v1/configs", 
            headers={"X-API-Key": "invalid-key-12345"}
        )
        self.assertEqual(response.status_code, 403)
        
        data = json.loads(response.data)
        self.assertEqual(data["status"], "error")
        self.assertEqual(data["message"], "Invalid API key")

    def test_auth_unvalidated_key(self):
        """Test accessing protected endpoint with unvalidated key (no credit card)."""
        # Create a key without validating it
        response = self.client.post(
            "/api/v1/auth/key",
            data=json.dumps({"email": "unvalidated@example.com"}),
            content_type="application/json"
        )
        data = json.loads(response.data)
        unvalidated_key = data["data"]["key"]
        
        # Try to access protected endpoint with unvalidated key
        response = self.client.get(
            "/api/v1/configs", 
            headers={"X-API-Key": unvalidated_key}
        )
        self.assertEqual(response.status_code, 403)
        
        data = json.loads(response.data)
        self.assertEqual(data["status"], "error")
        self.assertEqual(data["message"], "API key not validated - credit card required")

    def test_request_key_missing_email(self):
        """Test requesting a key without email."""
        response = self.client.post(
            "/api/v1/auth/key",
            data=json.dumps({}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertEqual(data["status"], "error")
        self.assertEqual(data["message"], "Email is required")

    def test_request_key_endpoint(self):
        """Test the key generation endpoint."""
        response = self.client.post(
            "/api/v1/auth/key",
            data=json.dumps({"email": "newuser@example.com"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertIn("key", data["data"])
        self.assertEqual(data["data"]["email"], "newuser@example.com")
        self.assertIn("message", data["data"])

    def test_validate_key_endpoint(self):
        """Test the key validation endpoint."""
        # Create a key first
        response = self.client.post(
            "/api/v1/auth/key",
            data=json.dumps({"email": "validate@example.com"}),
            content_type="application/json"
        )
        data = json.loads(response.data)
        key = data["data"]["key"]
        
        # Get the validation token from the key data
        from config_api.auth import APIKeyManager
        key_manager = APIKeyManager(storage_path=self.key_temp_dir)
        key_data = key_manager.get_key_data(key)
        validation_token = key_data.get("validation_token")
        
        # Validate the key using the token
        response = self.client.get(f"/api/v1/auth/validate?token={validation_token}")
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["message"], "API key validated successfully. Your key is now active and can be used to access the API.")


if __name__ == "__main__":
    unittest.main()
