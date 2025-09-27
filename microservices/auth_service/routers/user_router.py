# routers/user_router.py
from fastapi import APIRouter, Depends
from dependencies import get_user_service
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter()
# --- USERS ---
@router.post("/users")
def create_user(user_data: dict, db: Session = Depends(get_db), service=Depends(get_user_service)):
    return service["create_user"](db, user_data)

@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db), service=Depends(get_user_service)):
    return service["get_user"](db, user_id)

# --- ROLES ---
@router.post("/users/{user_id}/roles/{role_id}")
def assign_role_to_user(user_id: int, role_id: int, db: Session = Depends(get_db), service=Depends(get_user_service)):
    return service["assign_role_to_user"](db, user_id, role_id)

@router.post("/roles")
def create_role(role_data: dict, db: Session = Depends(get_db), service=Depends(get_user_service)):
    return service["create_role"](db, role_data)

# --- PERMISSIONS ---
@router.post("/permissions")
def create_permission(perm_data: dict, db: Session = Depends(get_db), service=Depends(get_user_service)):
    return service["create_permission"](db, perm_data)

@router.post("/roles/{role_id}/permissions/{perm_id}")
def assign_permission_to_role(role_id: int, perm_id: int, db: Session = Depends(get_db), service=Depends(get_user_service)):
    return service["assign_permission_to_role"](db, role_id, perm_id)
