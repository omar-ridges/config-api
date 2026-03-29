from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
import urllib.parse
from pathlib import Path

app = FastAPI()

def get_config_dir():
    """Get the configuration directory from environment variable or default."""
    config_dir = Path(os.getenv("CONFIG_DIR", "./config_files"))
    # Ensure the config directory exists
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

@app.get("/")
def read_root():
    return {"message": "Configuration File Server"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/config/")
@app.get("/config/{file_path:path}")
def get_config_file(file_path: str = ""):
    # Early security check: Detect path traversal attempts in the raw path
    if file_path and ".." in file_path:
        raise HTTPException(status_code=400, detail="Invalid file path")
    # Edge Case: Handle empty file path
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Decode URL encoded characters
    try:
        file_path = urllib.parse.unquote(file_path)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid file path encoding")
    
    # Additional security check: Detect obvious path traversal attempts
    if ".." in file_path or file_path.startswith("/") or "\\" in file_path:
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    # Get config directory dynamically
    config_dir = get_config_dir()
    
    # Construct full file path using Path for better security and consistency
    try:
        full_path = (config_dir / file_path).resolve()
        # Ensure the resolved path is within the config_dir to prevent directory traversal
        full_path.relative_to(config_dir.resolve())
    except (ValueError, OSError):
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    # Edge Case: Check if file exists
    if not full_path.exists():
        # Additional validation: Check if the path looks like a valid filename
        if not full_path.name or '.' not in full_path.name:
            raise HTTPException(status_code=400, detail="Invalid file name or missing extension")
        raise HTTPException(status_code=404, detail="File not found")
    
    # Edge Case: Check if path is a directory
    if full_path.is_dir():
        raise HTTPException(status_code=400, detail="Path is a directory, not a file")
    
    # Edge Case: Check if file is readable
    if not os.access(full_path, os.R_OK):
        raise HTTPException(status_code=403, detail="File is not accessible")
    
    return FileResponse(str(full_path))