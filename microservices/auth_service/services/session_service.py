import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Dict, Optional

from fastapi import HTTPException, status
from pymongo.errors import PyMongoError

from models.schemas import SessionCreate, SessionRead
from repositories.session_repository import SessionRepository


class SessionService(str, Enum):
    CREATE = "create_session"
    GET_BY_ID = "get_session_by_id"
    DELETE = "delete_session"
    INVALIDATE_EXPIRED = "invalidate_expired_sessions"


def create_session_fn(
    repo: SessionRepository,
    user_id: int,
    access_token: str,
    expires_in: int,
    refresh_token: Optional[str] = None,
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> SessionRead:
    """Crea una sesión, centralizando la generación de ID y fechas."""
    try:
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=expires_in)

        session_data = SessionCreate(
            session_id=session_id,
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            client_ip=client_ip,
            user_agent=user_agent,
        )
        
        return repo.create(session_data)
    except PyMongoError as e:
        # Captura errores específicos de la base de datos si es necesario
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session in database: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}",
        )


def get_session_fn(repo: SessionRepository, session_id: str) -> SessionRead:
    """Obtiene una sesión por su ID."""
    session = repo.get_by_session_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    return session


def delete_session_fn(repo: SessionRepository, session_id: str) -> bool:
    """Elimina una sesión por su ID."""
    deleted = repo.delete(session_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or already deleted",
        )
    return True


def invalidate_expired_sessions_fn(repo: SessionRepository) -> int:
    """Elimina todas las sesiones expiradas."""
    return repo.invalidate_expired()


def create_session_service() -> Dict[str, Callable]:
    """Factory que devuelve el diccionario de funciones del servicio de sesiones."""
    return {
        SessionService.CREATE: create_session_fn,
        SessionService.GET_BY_ID: get_session_fn,
        SessionService.DELETE: delete_session_fn,
        SessionService.INVALIDATE_EXPIRED: invalidate_expired_sessions_fn,
    }

