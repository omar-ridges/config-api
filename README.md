# Config API

An API that lets you pull your configuration files from anywhere.

## Overview

Config API is a RESTful API for storing, retrieving, and managing configuration files. It provides a simple interface for managing application configurations with support for CRUD operations.

## Features

- **RESTful API**: Clean, RESTful endpoints for configuration management
- **JSON Storage**: Store configurations as JSON files
- **Health Checks**: Built-in health check endpoint for monitoring
- **Validation**: Input validation for configuration names and data
- **Error Handling**: Comprehensive error handling with meaningful messages

## Project Structure

```
.
├── src/
│   └── config_api/          # Main application package
│       ├── __init__.py      # Package initialization
│       ├── app.py           # Flask application factory
│       ├── api.py           # API route definitions
│       ├── models.py        # Data models and business logic
│       ├── config.py        # Configuration classes
│       └── exceptions.py    # Custom exceptions
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_models.py       # Unit tests for models
│   └── test_api.py          # Integration tests for API
├── docs/                    # Documentation
├── pyproject.toml           # Project configuration
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
└── README.md                # This file
```

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/example/config-api.git
cd config-api

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```

### Using pip

```bash
pip install config-api
```

## Usage

### Running the Application

```bash
# Set environment variables (optional)
export SECRET_KEY="your-secret-key"
export CONFIG_STORAGE_PATH="/path/to/configs"

# Run the application
python -m flask --app src/config_api:create_app run
```

### API Endpoints

#### Health Check
```bash
GET /health
```

#### List Configurations
```bash
GET /api/v1/configs
```

#### Get Configuration
```bash
GET /api/v1/configs/<name>
```

#### Create Configuration
```bash
POST /api/v1/configs/<name>
Content-Type: application/json

{
  "key": "value",
  "nested": {
    "data": "value"
  }
}
```

#### Update Configuration
```bash
PUT /api/v1/configs/<name>
Content-Type: application/json

{
  "key": "updated_value"
}
```

#### Delete Configuration
```bash
DELETE /api/v1/configs/<name>
```

## Configuration

The application can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | `dev-secret-key` |
| `CONFIG_STORAGE_PATH` | Path to store configuration files | `./data` |
| `FLASK_ENV` | Flask environment | `production` |

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/config_api

# Run specific test file
pytest tests/test_models.py
```

### Code Quality

```bash
# Format code with black
black src/ tests/

# Check with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/
```

## License

MIT License - see LICENSE file for details.
