# services/session_service.py
from typing import Callable, List
from fastapi import HTTPException
from models.entities import SessionModel
from repositories.session_repository import SessionRepository

def create_session_fn(repo: SessionRepository, session: SessionModel) -> SessionModel:
    """Crear una nueva sesión"""
    try:
        return repo.create(session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")

def get_session_fn(repo: SessionRepository, session_id: str) -> SessionModel:
    session = repo.get_by_session_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

def delete_session_fn(repo: SessionRepository, session_id: str) -> bool:
    deleted = repo.delete(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found or already deleted")
    return True

def invalidate_expired_sessions_fn(repo: SessionRepository) -> int:
    return repo.invalidate_expired()
