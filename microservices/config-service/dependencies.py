# dependencies.py (actualizado para funcional)
from functools import lru_cache, partial
from typing import Dict, Callable, Any, List
from sqlalchemy.orm import Session
from fastapi import Depends
from models.schemas import ConfigurationCreate, ConfigurationResponse
from database import get_db
from repositories.configuration_repository import ConfigurationRepository
from services.configuration_service import (
    create_configuration_fn,
    create_configuration_service,
    get_all_configurations_fn,
    update_configuration_fn,
    with_error_handling,
    with_logging
)

# === DEPENDENCY INJECTION FUNCIONAL ===

@lru_cache()
def get_configuration_repository() -> ConfigurationRepository:
    """Factory para repositorio (singleton)"""
    return ConfigurationRepository()

def get_configuration_functions(
    repository: ConfigurationRepository = Depends(get_configuration_repository)
) -> Dict[str, Callable]:
    """
    Factory que retorna un diccionario de funciones de servicio
    
    En lugar de inyectar una clase, inyectamos un dict de funciones
    Cada función ya tiene el repository 'baked in' via partial application
    """
    return create_configuration_service(repository)

# === ALTERNATIVA: FUNCIONES INDIVIDUALES ===
def get_update_configuration_fn(
    repository: ConfigurationRepository = Depends(get_configuration_repository)
):
    return partial(update_configuration_fn, repository)
def get_create_configuration_fn(
    repository: ConfigurationRepository = Depends(get_configuration_repository)
) -> Callable[[Session, ConfigurationCreate], ConfigurationResponse]:
    """Inyecta solo la función de crear"""
    return partial(create_configuration_fn, repository)

def get_list_configurations_fn(
    repository: ConfigurationRepository = Depends(get_configuration_repository)
) -> Callable[[Session, int, int], List[ConfigurationResponse]]:
    """Inyecta solo la función de listar"""
    return partial(get_all_configurations_fn, repository)


# === ALTERNATIVA: ENHANCED FUNCTIONS ===

def get_enhanced_configuration_functions(
    repository: ConfigurationRepository = Depends(get_configuration_repository)
) -> Dict[str, Callable]:
    """Retorna funciones con error handling y logging aplicados"""
    base_functions = create_configuration_service(repository)
    
    # Aplicar decoradores funcionales a cada función
    return {
        'create': with_logging(with_error_handling(base_functions['create'])),
        'get_all': with_logging(with_error_handling(base_functions['get_all'])),
        'get_by_id': with_logging(with_error_handling(base_functions['get_by_id'])),
        'get_by_key': with_logging(with_error_handling(base_functions['get_by_key'])),
        'update': with_logging(with_error_handling(base_functions['update'])),
        'delete': with_logging(with_error_handling(base_functions['delete']))
    }

# === PATTERN: FUNCTION COMPOSITION ===

def compose_service_pipeline(repository: ConfigurationRepository):
    """
    Compone un pipeline de funciones para el servicio
    Pattern: Function Composition + Partial Application
    """
    def pipeline():
        # Base functions con repository aplicado
        base_fns = create_configuration_service(repository)
        
        # Pipeline de transformaciones
        enhanced_fns = {}
        for name, fn in base_fns.items():
            # Compone: logging ∘ error_handling ∘ base_function
            enhanced_fns[name] = with_logging(with_error_handling(fn))
        
        return enhanced_fns
    
    return pipeline()

def get_composed_configuration_service(
    repository: ConfigurationRepository = Depends(get_configuration_repository)
) -> Dict[str, Callable]:
    """Dependency que retorna el pipeline compuesto"""
    return compose_service_pipeline(repository)