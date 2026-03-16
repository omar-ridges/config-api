# Config API Usage Guide

This guide provides detailed information on using the Config API.

## Table of Contents

1. [Getting Started](#getting-started)
2. [API Reference](#api-reference)
3. [Examples](#examples)
4. [Error Handling](#error-handling)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Quick Start

1. Install the package:
   ```bash
   pip install config-api
   ```

2. Start the server:
   ```bash
   python run.py
   ```

3. Test the health endpoint:
   ```bash
   curl http://localhost:5000/health
   ```

## API Reference

### Health Check

Check if the API is running.

**Endpoint:** `GET /health`

**Response:**


{
  "status": "healthy",
  "service": "config-api"
}
```

### List Configurations

Get a list of all configuration names.

**Endpoint:** `GET /api/v1/configs`

**Response:**


{
  "status": "success",
  "data": ["config1", "config2", "config3"]
}
```

### Get Configuration

Retrieve a specific configuration.

**Endpoint:** `GET /api/v1/configs/{name}`

**Parameters:**
- `name` (path): Name of the configuration

**Response:**

{
  "status": "success",
  "data": {
    "key": "value"
  }
}
```

**Error Response (404):**

{
  "status": "error",
  "message": "Configuration 'name' not found"
}
```

### Create Configuration

Create a new configuration.

**Endpoint:** `POST /api/v1/configs/{name}`

**Parameters:**
- `name` (path): Name of the configuration
- Body: JSON object with configuration data

**Request:**

{
  "database": {
    "host": "localhost",
    "port": 5432
  },
  "debug": true
}
```

**Response (201):**

{
  "status": "success",
  "message": "Configuration 'name' created successfully"
}
```

### Update Configuration

Update an existing configuration.

**Endpoint:** `PUT /api/v1/configs/{name}`

**Parameters:**
- `name` (path): Name of the configuration
- Body: JSON object with updated configuration data

**Response:**

{
  "status": "success",
  "message": "Configuration 'name' updated successfully"
}
```

### Delete Configuration

Delete a configuration.

**Endpoint:** `DELETE /api/v1/configs/{name}`

**Parameters:**
- `name` (path): Name of the configuration

**Response:**

{
  "status": "success",
  "message": "Configuration 'name' deleted successfully"
}
```

## Examples

### Using cURL

```bash
# Create a configuration
curl -X POST http://localhost:5000/api/v1/configs/myapp \
  -H "Content-Type: application/json" \
  -d '{"debug": true, "version": "1.0.0"}'

# Get the configuration
curl http://localhost:5000/api/v1/configs/myapp

# Update the configuration
curl -X PUT http://localhost:5000/api/v1/configs/myapp \
  -H "Content-Type: application/json" \
  -d '{"debug": false, "version": "1.0.1"}'

# Delete the configuration
curl -X DELETE http://localhost:5000/api/v1/configs/myapp
```

### Using Python requests

```python
import requests

base_url = "http://localhost:5000/api/v1"

# Create a configuration
response = requests.post(
    f"{base_url}/configs/myapp",
    json={"debug": True, "version": "1.0.0"}
)
print(response.json())

# Get the configuration
response = requests.get(f"{base_url}/configs/myapp")
config = response.json()["data"]
print(config)

# Update the configuration
response = requests.put(
    f"{base_url}/configs/myapp",
    json={"debug": False, "version": "1.0.1"}
)
print(response.json())

# Delete the configuration
response = requests.delete(f"{base_url}/configs/myapp")
print(response.json())
```

## Error Handling

The API uses standard HTTP status codes:

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

All error responses include a JSON body with details:


{
  "status": "error",
  "message": "Description of the error"
}
```