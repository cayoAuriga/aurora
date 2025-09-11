# routers.py (versión corregida y unificada)
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Callable

from database import get_db
from dependencies import get_enhanced_configuration_functions
from models.schemas import ConfigurationCreate, ConfigurationUpdate, ConfigurationResponse

config_router = APIRouter()

# ==========================
# CRUD CONFIGURATIONS
# ==========================

@config_router.post("/configurations/", response_model=ConfigurationResponse)
async def create_configuration(
    config_data: ConfigurationCreate,
    db: Session = Depends(get_db),
    service_fns: Dict[str, Callable] = Depends(get_enhanced_configuration_functions),
):
    """Crear configuración"""
    return service_fns['create'](db, config_data)


@config_router.get("/configurations/", response_model=List[ConfigurationResponse])
async def list_configurations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    service_fns: Dict[str, Callable] = Depends(get_enhanced_configuration_functions),
):
    """Listar configuraciones con paginación"""
    return service_fns['get_all'](db, skip, limit)


@config_router.get("/configurations/{config_id}", response_model=ConfigurationResponse)
async def get_configuration(
    config_id: int,
    db: Session = Depends(get_db),
    service_fns: Dict[str, Callable] = Depends(get_enhanced_configuration_functions),
):
    """Obtener configuración por ID"""
    return service_fns['get_by_id'](db, config_id)


@config_router.get("/configurations/key/{config_key}", response_model=ConfigurationResponse)
async def get_configuration_by_key(
    config_key: str,
    environment: str = Query("development"),
    service_name: str = Query("global"),
    db: Session = Depends(get_db),
    service_fns: Dict[str, Callable] = Depends(get_enhanced_configuration_functions),
):
    """Obtener configuración por clave + entorno + servicio"""
    return service_fns['get_by_key'](db, config_key, environment, service_name)


@config_router.put("/configurations/{config_id}", response_model=ConfigurationResponse)
async def update_configuration(
    config_id: int,
    config_data: ConfigurationUpdate,
    db: Session = Depends(get_db),
    service_fns: Dict[str, Callable] = Depends(get_enhanced_configuration_functions),
):
    """Actualizar configuración"""
    return service_fns['update'](db, config_id, config_data)


@config_router.delete("/configurations/{config_id}")
async def delete_configuration(
    config_id: int,
    db: Session = Depends(get_db),
    service_fns: Dict[str, Callable] = Depends(get_enhanced_configuration_functions),
):
    """Eliminar configuración"""
    service_fns['delete'](db, config_id)
    return {"message": f"Configuration {config_id} deleted successfully"}
