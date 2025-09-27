import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI

# === PATH MANAGEMENT ===
# ⚠️ Temporal: en producción lo ideal es empaquetar e instalar shared/ como librería
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# === LOAD ENV VARS ===
load_dotenv()

# === INTERNAL IMPORTS ===
from shared.base_app import BaseService
from shared.settings import get_service_config, get_database_config, Service
from shared.aurora_logging import get_logger
from database import Base, engine  # Para inicializar DB
from routers.auth_router import auth_router, user_router, session_router

# === GET CONFIG FROM CENTRALIZED SETTINGS ===
config = get_service_config(Service.AUTH)

# === LOGGER ===
logger = get_logger(config.service_name)

# === CREATE BASE SERVICE ===
service = BaseService(Service.AUTH, version="1.0.0")

# === REGISTER ROUTERS ===
service.add_router(auth_router, prefix="/aurora_api/v1", tags=["authentication"])
service.add_router(user_router, prefix="/aurora_api/v1", tags=["users"])
service.add_router(session_router, prefix="/aurora_api/v1", tags=["sessions"])

# === FASTAPI APP ===
app: FastAPI = service.app

# === STARTUP EVENTS ===
@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    logger.info(f"🚀 Starting {config.service_name}...")
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
    logger.info(f"🛑 Shutting down {config.service_name}...")

# === ENTRYPOINT ===
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=config.host,               # ahora tomado de settings centralizados
        port=config.service_port,       # idem
        reload=config.debug,            # idem
    )