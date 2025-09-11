# services/configuration_service.py
"""
Servicios funcionales para configuraciones
Cada función es pura (dados los mismos inputs, produce los mismos outputs)
"""
import functools
from typing import List, Optional, Callable
from functools import partial
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.schemas import ConfigurationCreate, ConfigurationUpdate, ConfigurationResponse
from repositories.configuration_repository import ConfigurationRepository

# === FUNCIONES PURAS DE DOMINIO ===

def create_configuration_fn(
    repository: ConfigurationRepository,
    db: Session,
    config_data: ConfigurationCreate
) -> ConfigurationResponse:
    """Función pura para crear configuración"""
    try:
        db_config = repository.create(db, config_data)
        return ConfigurationResponse.from_orm(db_config)
    except Exception as e:
        if "duplicate" in str(e).lower() or "unique constraint" in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail=f"Configuration already exists for key: {config_data.config_key}"
            )
        raise HTTPException(status_code=500, detail=f"Error creating configuration: {str(e)}")

def get_all_configurations_fn(
    repository: ConfigurationRepository,
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[ConfigurationResponse]:
    """Función pura para obtener todas las configuraciones"""
    db_configs = repository.get_all(db, skip, limit)
    return [ConfigurationResponse.from_orm(config) for config in db_configs]

def get_configuration_by_id_fn(
    repository: ConfigurationRepository,
    db: Session,
    config_id: int
) -> ConfigurationResponse:
    """Función pura para obtener configuración por ID"""
    db_config = repository.get(db, config_id)
    if not db_config:
        raise HTTPException(status_code=404, detail=f"Configuration with ID {config_id} not found")
    return ConfigurationResponse.from_orm(db_config)

def get_configuration_by_key_fn(
    repository: ConfigurationRepository,
    db: Session,
    config_key: str,
    environment: str = "development",
    service_name: str = "global"
) -> ConfigurationResponse:
    """Función pura para obtener configuración por clave"""
    db_config = repository.get_by_key(db, config_key, environment, service_name)
    if not db_config:
        raise HTTPException(
            status_code=404,
            detail=f"Configuration not found: {config_key} in {environment}/{service_name}"
        )
    return ConfigurationResponse.from_orm(db_config)

def update_configuration_fn(
    repository: ConfigurationRepository,
    db: Session,
    config_id: int,
    config_data: ConfigurationUpdate
) -> ConfigurationResponse:
    """Función pura para actualizar configuración"""
    db_config = repository.get(db, config_id)
    if not db_config:
        raise HTTPException(status_code=404, detail=f"Configuration with ID {config_id} not found")
    
    updated_config = repository.update(db, db_config, config_data)
    return ConfigurationResponse.from_orm(updated_config)

def delete_configuration_fn(
    repository: ConfigurationRepository,
    db: Session,
    config_id: int
) -> bool:
    """Función pura para eliminar configuración"""
    deleted_config = repository.delete(db, config_id)
    if not deleted_config:
        raise HTTPException(status_code=404, detail=f"Configuration with ID {config_id} not found")
    return True

# === FUNCIONES FACTORY PARA INYECCIÓN DE DEPENDENCIAS ===

def create_configuration_service(repository: ConfigurationRepository):
    """
    Factory que retorna funciones parcialmente aplicadas
    Esto es similar a currying - aplicamos el repository y retornamos funciones
    que solo necesitan db y los parámetros específicos
    """
    return {
        'create': partial(create_configuration_fn, repository),
        'get_all': partial(get_all_configurations_fn, repository),
        'get_by_id': partial(get_configuration_by_id_fn, repository),
        'get_by_key': partial(get_configuration_by_key_fn, repository),
        'update': partial(update_configuration_fn, repository),
        'delete': partial(delete_configuration_fn, repository)
    }

# === ALTERNATIVA MÁS ELEGANTE CON CLASES FUNCIONALES ===

class ConfigurationServiceFunctions:
    """
    Contenedor de funciones - no es OOP tradicional, es un namespace funcional
    Todas las funciones son static y puras
    """
    
    @staticmethod
    def with_repository(repository: ConfigurationRepository):
        """
        Retorna un diccionario de funciones parcialmente aplicadas
        Pattern: Dependency Injection funcional
        """
        return {
            'create': lambda db, config_data: create_configuration_fn(repository, db, config_data),
            'get_all': lambda db, skip=0, limit=100: get_all_configurations_fn(repository, db, skip, limit),
            'get_by_id': lambda db, config_id: get_configuration_by_id_fn(repository, db, config_id),
            'get_by_key': lambda db, config_key, environment="development", service_name="global": 
                get_configuration_by_key_fn(repository, db, config_key, environment, service_name),
            'update': lambda db, config_id, config_data: update_configuration_fn(repository, db, config_id, config_data),
            'delete': lambda db, config_id: delete_configuration_fn(repository, db, config_id)
        }

# === PATTERN: HIGHER-ORDER FUNCTIONS ===

def with_error_handling(service_fn: Callable) -> Callable:
    """
    Decorator funcional para manejo de errores
    Higher-order function que toma una función y retorna una función mejorada
    """
    def wrapper(*args, **kwargs):
        try:
            return service_fn(*args, **kwargs)
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Log y convierte otros errores
            import logging
            fn_name = service_fn.func.__name__ if isinstance(service_fn, functools.partial) else service_fn.__name__
            logging.error(f"Service error in {fn_name}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    return wrapper

def with_logging(service_fn: Callable) -> Callable:
    """Decorator funcional para logging"""
    def wrapper(*args, **kwargs):
        import logging
        logging.info(f"Executing {service_fn.__name__} with args: {args[2:] if len(args) > 2 else 'no args'}")
        result = service_fn(*args, **kwargs)
        logging.info(f"Completed {service_fn.__name__}")
        return result
    return wrapper

# Composición de decorators funcionales
enhanced_create_configuration = with_logging(with_error_handling(create_configuration_fn))