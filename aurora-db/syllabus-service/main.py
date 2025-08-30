"""
Syllabus Service - Core syllabus domain logic
"""
import os
from fastapi import FastAPI
import uvicorn

from shared.base_app import create_service_app


def create_app() -> FastAPI:
    """Create Syllabus Service application"""
    service = create_service_app(
        service_name="syllabus-service",
        version="1.0.0",
        description="Syllabus management service with CQRS pattern"
    )
    
    # TODO: Add syllabus routes
    # TODO: Add database connection
    # TODO: Add CQRS commands and queries
    # TODO: Add event publishing
    
    return service.get_app()


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )