from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import os

app = FastAPI(title="Config API", description="An API that lets you pull configuration files from anywhere")

# In-memory storage for configurations
# In a real implementation, this would be backed by a database or file system
configs: Dict[str, Dict[str, Any]] = {
    "default": {
        "app_name": "Config API",
        "version": "1.0.0",
        "debug": False
    },
    "database": {
        "host": "localhost",
        "port": 5432,
        "username": "admin",
        "password": "secret"
    }
}


class ConfigResponse(BaseModel):
    name: str
    config: Dict[str, Any]


class ConfigListResponse(BaseModel):
    configs: list[str]


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint returning API information."""
    return {"message": "Config API", "version": "1.0.0"}


@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/config", response_model=ConfigListResponse)
async def list_configs():
    """List all available configuration names."""
    return ConfigListResponse(configs=list(configs.keys()))


@app.get("/config/{config_name}", response_model=ConfigResponse)
async def get_config(config_name: str):
    """Get a specific configuration by name."""
    if config_name not in configs:
        raise HTTPException(status_code=404, detail=f"Configuration '{config_name}' not found")
    return ConfigResponse(name=config_name, config=configs[config_name])


@app.post("/config/{config_name}", response_model=ConfigResponse)
async def create_config(config_name: str, config: Dict[str, Any]):
    """Create or update a configuration."""
    configs[config_name] = config
    return ConfigResponse(name=config_name, config=config)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
