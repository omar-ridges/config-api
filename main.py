from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
import urllib.parse
from pathlib import Path

app = FastAPI()

# Configuration
CONFIG_FILES_DIR = Path("config_files")
CONFIG_FILES_DIR.mkdir(exist_ok=True)

# Set default config directory
app.config_dir = CONFIG_FILES_DIR

@app.get("/")
def read_root():
    return {"message": "Config File Server"}

@app.get("/config/{file_path:path}")
def get_config_file(file_path: str):
    # Edge Case: Handle empty file path
    if not file_path:
        raise HTTPException(status_code=400, detail="File path is required")
    
    # Decode URL encoded characters
    decoded_path = urllib.parse.unquote(file_path)
    
    # Use Path for better path handling
    try:
        requested_path = Path(decoded_path)
        # Create a safe path by joining with config directory
        config_dir = Path(app.config_dir)
        full_path = (config_dir / requested_path).resolve()
    except (ValueError, IndexError):
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    # Prevent directory traversal attacks by ensuring full_path is within config directory
    try:
        config_dir = Path(app.config_dir)
        full_path.relative_to(config_dir)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    # Edge Case: Check if file exists
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Edge Case: Check if path is a directory
    if full_path.is_dir():
        raise HTTPException(status_code=400, detail="Path is a directory, not a file")
    
    # Edge Case: Check if file is readable
    if not os.access(full_path, os.R_OK):
        raise HTTPException(status_code=403, detail="File is not accessible")
    
    # Set appropriate content-type based on file extension
    media_type = None
    if full_path.suffix.lower() == '.json':
        media_type = 'application/json'
    elif full_path.suffix.lower() == '.yaml' or full_path.suffix.lower() == '.yml':
        media_type = 'application/x-yaml'
    elif full_path.suffix.lower() == '.txt':
        media_type = 'text/plain'
    
    return FileResponse(str(full_path), media_type=media_type)

@app.get("/configs")
def list_config_files():
    """List all config files in the config directory"""
    try:
        # Ensure app.config_dir is a Path object
        config_dir = Path(app.config_dir)
        files = []
        for item in config_dir.iterdir():
            if item.is_file():
                files.append(item.name)
        return {"files": sorted(files)}
    except Exception:
        raise HTTPException(status_code=500, detail="Error listing config files")