from fastapi.testclient import TestClient
from main import app
import tempfile
import os

# Create a test setup similar to the failing test
test_dir = tempfile.mkdtemp()
with open(os.path.join(test_dir, "config1.json"), "w") as f:
    f.write('{"key": "value1"}')

app.config_dir = test_dir
client = TestClient(app)

# Test the /configs endpoint
response = client.get("/configs")
print(f"Status code: {response.status_code}")
print(f"Response: {response.text}")
print(f"Headers: {response.headers}")

# Clean up
import shutil
shutil.rmtree(test_dir)