import unittest
from fastapi.testclient import TestClient
from main import app
import os
import tempfile
import shutil

class TestConfigFileServer(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        # Create some test config files
        self.test_files = {
            "config1.json": '{"key": "value1"}',
            "config2.yaml": 'key: value2',
            "config3.txt": 'simple text config'
        }
        for filename, content in self.test_files.items():
            with open(os.path.join(self.test_dir, filename), 'w') as f:
                f.write(content)
        
        # Update the app's config directory to point to our test directory
        app.config_dir = self.test_dir

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)

    def test_get_existing_config_file_json(self):
        response = self.client.get("/config/config1.json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, self.test_files["config1.json"])
        # Check that content-type is set correctly
        self.assertIn("application/json", response.headers["content-type"])

    def test_get_existing_config_file_yaml(self):
        response = self.client.get("/config/config2.yaml")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, self.test_files["config2.yaml"])
        # Check that content-type is set correctly
        self.assertIn("application/x-yaml", response.headers["content-type"])

    def test_get_existing_config_file_txt(self):
        response = self.client.get("/config/config3.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, self.test_files["config3.txt"])
        # Check that content-type is set correctly
        self.assertIn("text/plain", response.headers["content-type"])

    def test_get_nonexistent_config_file(self):
        response = self.client.get("/config/nonexistent.json")
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.json())

    def test_get_config_file_with_special_characters(self):
        # Create a file with special characters in the name
        special_filename = "config-special_chars.json"
        special_content = '{"special": "chars-test"}'
        with open(os.path.join(self.test_dir, special_filename), 'w') as f:
            f.write(special_content)
        
        response = self.client.get(f"/config/{special_filename}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, special_content)

    def test_list_config_files(self):
        response = self.client.get("/configs")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("files", data)
        file_list = data["files"]
        for filename in self.test_files.keys():
            self.assertIn(filename, file_list)

    def test_list_config_files_empty_directory(self):
        # Create an empty directory and test listing
        empty_dir = tempfile.mkdtemp()
        app.config_dir = empty_dir
        
        response = self.client.get("/configs")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("files", data)
        self.assertEqual(data["files"], [])
        
        # Clean up
        shutil.rmtree(empty_dir)
        # Restore config directory
        app.config_dir = self.test_dir

    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Config File Server"})

if __name__ == "__main__":
    unittest.main()