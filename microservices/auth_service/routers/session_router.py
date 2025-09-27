# routers/session_router.py
from fastapi import APIRouter, Depends
from repositories.session_repository import SessionRepository
from services.session_service import create_session_service
from dependencies import repository_factory, service_functions_factory
from models.entities import SessionModel
from pymongo import MongoClient

client = MongoClient("mongodb+srv://<user>:<pass>@cluster.mongodb.net/test")
collection = client.auth_service.sessions

session_repo_dep = repository_factory(SessionRepository, collection)
get_session_functions = service_functions_factory(create_session_service, session_repo_dep)

router = APIRouter()

@router.post("/sessions")
def create_session(session: SessionModel, service_fns = Depends(get_session_functions)):
    return service_fns["create"](session)

@router.get("/sessions/{session_id}")
def get_session(session_id: str, service_fns = Depends(get_session_functions)):
    return service_fns["get"](session_id)

@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, service_fns = Depends(get_session_functions)):
    return service_fns["delete"](session_id)

@router.post("/sessions/invalidate_expired")
def invalidate_expired(service_fns = Depends(get_session_functions)):
    return {"deleted_count": service_fns["invalidate_expired"]()}
