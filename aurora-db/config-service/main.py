"""
Configuration Service - Centralized configuration management
"""
import os
from fastapi import FastAPI
import uvicorn

from shared.base_app import create_service_app


def create_app() -> FastAPI:
    """Create Configuration Service application"""
    service = create_service_app(
        service_name="config-service",
        version="1.0.0",
        description="Centralized configuration management service"
    )
    
    # TODO: Add configuration routes
    # TODO: Add configuration storage
    # TODO: Add environment-specific settings
    # TODO: Add feature flags
    
    return service.get_app()


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8004))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )