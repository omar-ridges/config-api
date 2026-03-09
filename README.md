# Config API

An API that lets you pull configuration files from anywhere.

## Features

- List all available configurations
- Get specific configuration by name
- Create and update configurations
- Health check endpoint

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/config` | List all configurations |
| GET | `/config/{name}` | Get specific configuration |
| POST | `/config/{name}` | Create/update configuration |

## Running the API

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

## Running Tests

```bash
pytest test_main.py -v
```

## Example Usage

```bash
# List all configurations
curl http://localhost:8000/config

# Get a specific configuration
curl http://localhost:8000/config/default

# Create a new configuration
curl -X POST http://localhost:8000/config/myapp \
  -H "Content-Type: application/json" \
  -d '{"key": "value", "setting": true}'
```
