"""
API Gateway Service - Entry point for all client requests
"""
import os
from fastapi import FastAPI
import uvicorn

from shared.base_app import create_service_app


def create_app() -> FastAPI:
    """Create API Gateway application"""
    service = create_service_app(
        service_name="api-gateway",
        version="1.0.0",
        description="API Gateway for microservices routing and cross-cutting concerns"
    )
    
    # TODO: Add routing configuration
    # TODO: Add authentication middleware
    # TODO: Add rate limiting
    # TODO: Add circuit breaker
    
    return service.get_app()


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )