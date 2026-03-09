
import sys, pytest, collections, collections.abc, urllib3.exceptions, _pytest.pytester, numpy;
collections.Mapping = collections.abc.Mapping;
collections.MutableMapping = collections.abc.MutableMapping;
collections.MutableSet = collections.abc.MutableSet;
collections.Sequence = collections.abc.Sequence;
collections.Callable = collections.abc.Callable;
collections.Iterable = collections.abc.Iterable;
collections.Iterator = collections.abc.Iterator;
urllib3.exceptions.SNIMissingWarning = urllib3.exceptions.DependencyWarning;
pytest.RemovedInPytest4Warning = DeprecationWarning;
_pytest.pytester.Testdir = _pytest.pytester.Pytester;
numpy.PINF = numpy.inf;
numpy.unicode_ = numpy.str_;
numpy.bytes_ = numpy.bytes_;
numpy.float_ = numpy.float64;
numpy.string_ = numpy.bytes_;
numpy.NaN = numpy.nan;


import pytest
from fastapi.testclient import TestClient
from main import app, configs

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Config API"
    assert data["version"] == "1.0.0"


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_list_configs():
    """Test listing all configurations."""
    response = client.get("/config")
    assert response.status_code == 200
    data = response.json()
    assert "configs" in data
    assert isinstance(data["configs"], list)
    assert "default" in data["configs"]
    assert "database" in data["configs"]


def test_get_config_success():
    """Test getting a specific configuration that exists."""
    response = client.get("/config/default")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "default"
    assert "config" in data
    assert data["config"]["app_name"] == "Config API"


def test_get_config_not_found():
    """Test getting a configuration that does not exist."""
    response = client.get("/config/nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_create_config():
    """Test creating a new configuration."""
    new_config = {
        "api_key": "test123",
        "timeout": 30
    }
    response = client.post("/config/test_config", json=new_config)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_config"
    assert data["config"] == new_config
    
    # Verify it was actually stored
    response = client.get("/config/test_config")
    assert response.status_code == 200
    data = response.json()
    assert data["config"]["api_key"] == "test123"


def test_update_config():
    """Test updating an existing configuration."""
    updated_config = {
        "app_name": "Updated Config API",
        "version": "2.0.0"
    }
    response = client.post("/config/default", json=updated_config)
    assert response.status_code == 200
    data = response.json()
    assert data["config"]["app_name"] == "Updated Config API"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
