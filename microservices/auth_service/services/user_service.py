# services/user_service.py
from typing import Dict, Callable
from fastapi import HTTPException
from models.entities import User, Role, Permission
from repositories.user_repository import UserRepository
from repositories.role_repository import RoleRepository
from repositories.permission_repository import PermissionRepository
from sqlalchemy.orm import Session

def create_user_fn(repo: UserRepository, db: Session, data: UserCreate) -> UserRead:
    if repo.get_by_email(db, data.email):
        raise HTTPException(400, "Email already exists")
    user = repo.create(db, data)
    return UserRead.from_orm(user)

def get_user_fn(repo: UserRepository, db: Session, user_id: int) -> UserRead:
    user = repo.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.from_orm(user)

def assign_role_to_user_fn(user_repo: UserRepository, role_repo: RoleRepository, db: Session, user_id: int, role_id: int) -> UserRead:
    user = user_repo.get(db, user_id)
    role = role_repo.get(db, role_id)
    if not user or not role:
        raise HTTPException(status_code=404, detail="User or Role not found")
    if role not in user.roles:
        user.roles.append(role)
        db.commit()
        db.refresh(user)
    return UserRead.from_orm(user)

def create_role_fn(repo: RoleRepository, db: Session, role_data: dict) -> RoleRead:
    return RoleRead.from_orm(repo.create(db, role_data))

def create_permission_fn(repo: PermissionRepository, db: Session, perm_data: dict) -> PermissionRead:
    return PermissionRead.from_orm(repo.create(db, perm_data))

def assign_permission_to_role_fn(role_repo: RoleRepository, perm_repo: PermissionRepository, db: Session, role_id: int, perm_id: int) -> RoleRead:
    role = role_repo.get(db, role_id)
    perm = perm_repo.get(db, perm_id)
    if not role or not perm:
        raise HTTPException(status_code=404, detail="Role or Permission not found")
    return RoleRead.from_orm(role_repo.assign_permission(db, role, perm))

def create_session_fn(repo: SessionRepository, data: SessionCreate) -> SessionRead:
    return SessionRead.from_orm(repo.create(data))

def get_session_fn(repo: SessionRepository, session_id: str) -> SessionRead:
    session = repo.get_by_session_id(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    return SessionRead.from_orm(session)

# Factory de servicios
def create_user_service(user_repo: UserRepository, role_repo: RoleRepository, perm_repo: PermissionRepository, session_repo: SessionRepository) -> Dict[str, Callable]:
    return {
        "create_user": lambda db, data: create_user_fn(user_repo, db, data),
        "get_user": lambda db, uid: get_user_fn(user_repo, db, uid),
        "assign_role_to_user": lambda db, uid, rid: assign_role_to_user_fn(user_repo, role_repo, db, uid, rid),
        "create_role": lambda db, data: create_role_fn(role_repo, db, data),
        "create_permission": lambda db, data: create_permission_fn(perm_repo, db, data),
        "assign_permission_to_role": lambda db, rid, pid: assign_permission_to_role_fn(role_repo, perm_repo, db, rid, pid),
        "create_session": lambda data: create_session_fn(session_repo, data),
        "get_session": lambda session_id: get_session_fn(session_repo, session_id)
    }
