import unittest
from fastapi.testclient import TestClient
from main import app
import os
import tempfile
import json

class TestConfigEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Create a temporary directory for test config files
        self.test_dir = tempfile.mkdtemp()
        # Set the config directory environment variable
        os.environ["CONFIG_DIR"] = self.test_dir
        
        # Create sample config files
        self.sample_json = {"key": "value", "number": 42}
        self.sample_text = "This is a sample config file\nWith multiple lines"
        
        with open(os.path.join(self.test_dir, "config.json"), "w") as f:
            json.dump(self.sample_json, f)
            
        with open(os.path.join(self.test_dir, "config.txt"), "w") as f:
            f.write(self.sample_text)
            
        with open(os.path.join(self.test_dir, "nested_config.yaml"), "w") as f:
            f.write("database:\n  host: localhost\n  port: 5432")

    def tearDown(self):
        # Clean up temporary files
        for file in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, file))
        os.rmdir(self.test_dir)
        # Remove environment variable
        if "CONFIG_DIR" in os.environ:
            del os.environ["CONFIG_DIR"]

    def test_get_json_config(self):
        response = self.client.get("/config/config.json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.sample_json)

    def test_get_text_config(self):
        response = self.client.get("/config/config.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, self.sample_text)

    def test_get_yaml_config(self):
        response = self.client.get("/config/nested_config.yaml")
        self.assertEqual(response.status_code, 200)
        # YAML should be returned as plain text
        self.assertIn("database:", response.text)
        self.assertIn("localhost", response.text)

    def test_get_nonexistent_config(self):
        response = self.client.get("/config/nonexistent.conf")
        self.assertEqual(response.status_code, 404)

    def test_get_config_without_extension(self):
        response = self.client.get("/config/config")
        self.assertEqual(response.status_code, 400)

    def test_get_config_with_path_traversal_attempt(self):
        response = self.client.get("/config/../../../etc/passwd")
        self.assertEqual(response.status_code, 400)

    def test_get_config_empty_filename(self):
        response = self.client.get("/config/")
        self.assertEqual(response.status_code, 404)

    def test_health_check_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})

    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()