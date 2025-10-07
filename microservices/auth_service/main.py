import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI
from contextlib import asynccontextmanager # Para lifespan manager

# === PATH MANAGEMENT ===
# ⚠️ Temporal: en producción lo ideal es empaquetar e instalar shared/ como librería
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# === LOAD ENV VARS ===
load_dotenv()

# === INTERNAL IMPORTS ===
from shared.base_app import BaseService
from shared.settings import Service, get_service_config
from shared.aurora_logging import get_logger
from database import Base, engine  # Para inicializar DB
from routers.auth_router import auth_router
from routers.user_router import user_router
from routers.role_router import role_router
from routers.permission_router import permission_router


# === GET CONFIG FROM CENTRALIZED SETTINGS ===
config = get_service_config(Service.AUTH)

# === LOGGER ===
logger = get_logger(config.service_name)

# === 2. DEFINIR EL LIFESPAN MANAGER ===
@asynccontextmanager
async def service_specific_lifespan(app: FastAPI):
    # Lógica específica del servicio de autenticación
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database initialized for auth-service")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    yield  # <-- La aplicación se ejecuta aquí

    # --- Código que se ejecuta DESPUÉS de que la aplicación haya terminado de aceptar peticiones ---
    logger.info(f"🛑 Shutting down {config.service_name}...")


# === CREATE BASE SERVICE Y REGISTRAR EL LIFESPAN ===
# 3. Pasa la función lifespan al constructor de tu servicio/app
service = BaseService(Service.AUTH, version="1.0.0", lifespan=service_specific_lifespan)

# === REGISTER ROUTERS ===
service.add_router(auth_router, prefix="/aurora_api/v1", tags=["authentication"])
service.add_router(user_router, prefix="/aurora_api/v1", tags=["users"])
service.add_router(role_router, prefix="/aurora_api/v1", tags=["roles"])
service.add_router(permission_router, prefix="/aurora_api/v1", tags=["permissions"])
# ... (añade tus otros routers aquí)

# === FASTAPI APP ===
app: FastAPI = service.app

# === ENTRYPOINT ===
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=config.host,
        port=config.service_port,
        reload=config.debug,
    )