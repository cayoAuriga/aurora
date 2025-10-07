# dependencies.py
from functools import lru_cache
from fastapi import Depends
from typing import Generator, Callable, Dict

# Importa tus servicios y el UoW
from repositories.unit_of_work import AbstractUnitOfWork, SqlAlchemyUnitOfWork
from services.user_service import create_user_service
from services.auth_service import create_auth_service # Asegúrate de crear este factory
from services.role_service import create_role_service
from services.session_service import create_session_service
from services.permission_service import create_permission_service
from repositories.session_repository import SessionRepository # Mongo repo
from pymongo.collection import Collection # Para el tipo
from shared.settings import GoogleOAuthConfig, get_google_oauth_config, get_mongo_config, MongoConfig


# 1. Dependencia para el Unit of Work
def get_uow() -> Generator[AbstractUnitOfWork, None, None]:
    """Dependency que proporciona una instancia del UnitOfWork."""
    uow = SqlAlchemyUnitOfWork()
    try:
        yield uow
    finally:
        # El __exit__ del UoW ya maneja el cierre de la sesión
        pass

def get_session_repository(
    db: MongoConfig = Depends(get_mongo_config)
) -> SessionRepository:
    """
    Dependency que proporciona una instancia de SessionRepository.
    Obtiene la colección de la base de datos inyectada.
    """
    collection = db.sessions # Asume que tu colección se llama 'sessions'
    return SessionRepository(collection)

@lru_cache()
def get_google_oauth_settings() -> GoogleOAuthConfig:
    return get_google_oauth_config()

# 2. Dependencia para el servicio de sesiones
def get_session_service(
    repo: SessionRepository = Depends(get_session_repository)
) -> Dict[str, Callable]:
    service_fns = create_session_service()
    # Pre-configuramos el repo en las funciones que lo necesiten
    return {
        key: functools.partial(fn, repo=repo) if "repo" in fn.__code__.co_varnames else fn
        for key, fn in service_fns.items()
    }

# --- La nueva dependencia para el servicio de autenticación ---
def get_auth_service(
    # Resuelve aquí las dependencias que la factoría necesita
    session_service: Dict[str, Callable] = Depends(get_session_service),
    session_repo = Depends(get_session_repository),
    oauth_config: GoogleOAuthConfig = Depends(get_google_oauth_settings),
) -> Dict[str, Callable]:
    """
    Crea y devuelve el servicio de autenticación con todas sus dependencias inyectadas.
    """
    return create_auth_service(
        session_service=session_service,
        session_repo=session_repo,
        config=oauth_config,
    )

# 3. Dependencias de servicios simplificadas
@lru_cache()
def get_user_service():
    return create_user_service()

@lru_cache()
def get_role_service():    
    return create_role_service()

@lru_cache()
def get_permission_service():
    return create_permission_service()