"""
Subject Service - Subject management and metadata
"""
import os
from fastapi import FastAPI
import uvicorn

from shared.base_app import create_service_app


def create_app() -> FastAPI:
    """Create Subject Service application"""
    service = create_service_app(
        service_name="subject-service",
        version="1.0.0",
        description="Subject management service with CRUD operations"
    )
    
    # TODO: Add subject routes
    # TODO: Add database connection
    # TODO: Add CQRS commands and queries
    # TODO: Add event publishing
    
    return service.get_app()


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8002))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )