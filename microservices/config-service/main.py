"""
Configuration Service - Centralized configuration and feature flags management
"""
from fastapi import APIRouter

from shared.base_app import BaseService, create_service
from shared.config import get_config
from shared.aurora_logging import get_logger

from .routers.configuration_router import router as configuration_router
from .routers.feature_flag_router import router as feature_flag_router
from .routers.discovery_router import router as discovery_router

# Service configuration
config = get_config("config-service")
logger = get_logger("config-service")

# Create service instance
service = create_service(
    service_name="config-service",
    config=config,
    title="Configuration Service",
    description="Centralized configuration and feature flags management service"
)

# Root router
root_router = APIRouter()


@root_router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Configuration Service is running",
        "service": "config-service",
        "version": "1.0.0",
        "endpoints": {
            "configurations": "/api/v1/configurations",
            "feature_flags": "/api/v1/feature-flags",
            "health": "/health",
            "docs": "/docs"
        }
    }


@root_router.get("/status")
async def status():
    """Service status endpoint"""
    return {
        "service": "config-service",
        "status": "healthy",
        "features": [
            "Configuration Management",
            "Feature Flags",
            "Configuration History",
            "Environment-specific Configs",
            "Service-specific Configs"
        ]
    }


# Add routers to service
service.add_router(root_router, prefix="", tags=["root"])
service.add_router(configuration_router, prefix="/api/v1", tags=["configurations"])
service.add_router(feature_flag_router, prefix="/api/v1", tags=["feature-flags"])
service.add_router(discovery_router, prefix="/api/v1", tags=["service-discovery"])

# Export the FastAPI app
app = service.app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=config.service_port,
        reload=config.debug
    )