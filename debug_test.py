from fastapi.testclient import TestClient
from main import app
import os
import tempfile

# Setup
os.environ["CONFIG_DIR"] = tempfile.mkdtemp()
client = TestClient(app)

# Test
response = client.get("/config/../../../etc/passwd")
print("Status:", response.status_code, response.json())