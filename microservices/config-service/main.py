"""
Configuration Service - Centralized configuration and feature flags management
Refactored modular version
"""

import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI

# === PATH MANAGEMENT ===
# ⚠️ Temporal: en producción usa un paquete instalable
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# === LOAD ENV VARS ===
load_dotenv()

# === INTERNAL IMPORTS ===
from shared.base_app import BaseService
from shared.aurora_logging import get_logger
from config import service_config
from database import Base, engine  # Para inicializar DB
from routers import config_router

# === LOGGER ===
logger = get_logger("config-service")

# === CREATE BASE SERVICE ===
service = BaseService(
    service_name=service_config.service_name,
    config=service_config,
    title="Configuration Service",
    description="Centralized configuration and feature flags management service with TiDB integration",
)

# === REGISTER ROUTERS ===
service.add_router(config_router, prefix="/aurora_api/v1", tags=["configurations"])
# service.add_router(flag_router, prefix="/aurora_api/v1", tags=["feature-flags"])

# === FASTAPI APP ===
app: FastAPI = service.app

# === STARTUP EVENTS ===
@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    logger.info("🚀 Starting Configuration Service...")
    # Crear tablas si no existen (solo para entornos dev/test)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down Configuration Service...")


# === ENTRYPOINT ===
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=service_config.service_port,
        reload=service_config.debug,
    )
