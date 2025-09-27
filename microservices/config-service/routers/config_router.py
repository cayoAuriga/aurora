# config_router.py
import os, sys
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Callable
from shared.sql_logging import with_sql_logging
from database import get_db
from dependencies import (
    repository_factory,    
    pipeline_factory,
    service_functions_factory,
)
from models.schemas import ConfigurationCreate, ConfigurationUpdate, ConfigurationResponse
from repositories.configuration_repository import ConfigurationRepository
from services.configuration_service import (
    create_configuration_service,
    with_error_handling,
    with_logging,
)
from shared.aurora_logging import get_logger
# === PATH CONFIG ===
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# === ENV ===
load_dotenv()
config_router = APIRouter()
# === LOGGER ===
logger = get_logger(__name__)

# === REPOSITORY DEPENDENCY ===
get_configuration_repository = repository_factory(ConfigurationRepository)

# === SERVICE FUNCTIONS DEPENDENCY ===
get_configuration_functions = service_functions_factory(
    create_configuration_service,
    get_configuration_repository
)

# === PIPELINE DEPENDENCY ===
get_composed_configuration_service = pipeline_factory(
    create_configuration_service,
    [with_error_handling, with_logging, with_sql_logging],
    get_configuration_repository
)
# ==========================
# CRUD CONFIGURATIONS
# ==========================


@config_router.post("/configurations", response_model=ConfigurationResponse)
def create_configuration(
    config_data: ConfigurationCreate,
    db: Session = Depends(get_db),
    service_fns: dict = Depends(get_configuration_functions)
):
    return service_fns["create"](db, config_data)


@config_router.get("/configurations", response_model=list[ConfigurationResponse])
def list_configurations(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    fns: dict = Depends(get_configuration_functions)
):
    return fns["get_all"](db, skip, limit)


@config_router.get("/configurations/{config_id}", response_model=ConfigurationResponse)
async def get_configuration(
    config_id: int,
    db: Session = Depends(get_db),
    service_fns: Dict[str, Callable] = Depends(get_configuration_functions),
):
    """Obtener configuración por ID"""
    return service_fns['get_by_id'](db, config_id)


@config_router.get("/configurations/key/{config_key}", response_model=ConfigurationResponse)
async def get_configuration_by_key(
    config_key: str,
    environment: str = Query("development"),
    service_name: str = Query("global"),
    db: Session = Depends(get_db),
    service_fns: Dict[str, Callable] = Depends(get_configuration_functions),
):
    """Obtener configuración por clave + entorno + servicio"""
    return service_fns['get_by_key'](db, config_key, environment, service_name)


@config_router.put("/configurations/{config_id}", response_model=ConfigurationResponse)
def update_configuration(
    config_id: int,
    config: ConfigurationCreate,
    db: Session = Depends(get_db),    
    fns: dict = Depends(get_composed_configuration_service)
):
    return fns["update"](db, config_id, config)


@config_router.delete("/configurations/{config_id}")
async def delete_configuration(
    config_id: int,
    db: Session = Depends(get_db),
    service_fns: Dict[str, Callable] = Depends(get_configuration_functions),
):
    """Eliminar configuración"""
    service_fns['delete'](db, config_id)
    return {"message": f"Configuration {config_id} deleted successfully"}
