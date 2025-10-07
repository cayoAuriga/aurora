# services/user_service.py
from typing import Dict, Callable, List, Optional
from enum import Enum
from fastapi import HTTPException
from models.entities import User, Role, Permission
from models.schemas import UserCreate, UserRead, UserUpdate
from repositories.unit_of_work import AbstractUnitOfWork
from repositories.user_repository import UserRepository
from repositories.role_repository import RoleRepository
from repositories.permission_repository import PermissionRepository
from sqlalchemy.orm import Session

class UserService(str, Enum):
    CREATE = "create_user"
    READ = "get_user"
    UPDATE = "update_user"
    DELETE = "delete_user"
    LIST = "list_users"
    ASSIGN_ROLE = "assign_role_to_user"

def create_user_fn(uow: AbstractUnitOfWork, data: UserCreate) -> UserRead:
    with uow:
        if uow.users.get_by_email(data.email):
            raise HTTPException(400, "Email already exists")
        user = uow.users.create(data)
        # El commit se hace automáticamente al salir del 'with'
    return UserRead.from_orm(user)


def get_user_fn(uow: AbstractUnitOfWork, user_id: int) -> UserRead:
    with uow:  # Usamos 'with' para asegurar que la sesión se cierre
        user = uow.users.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    return UserRead.from_orm(user)


def update_user_fn(uow: AbstractUnitOfWork, user_id: int, data: UserUpdate) -> UserRead:
    with uow:
        user = uow.users.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user = uow.users.update(user, data)
    return UserRead.from_orm(user)


def delete_user_fn(uow: AbstractUnitOfWork, user_id: int) -> UserRead:
    with uow:
        user = uow.users.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        uow.users.delete(user_id)
    return UserRead.from_orm(user)    


def list_users_fn(
    uow: AbstractUnitOfWork, skip: int = 0, limit: int = 100
) -> List[UserRead]:
    with uow:
        users = uow.users.get_all(skip=skip, limit=limit)
    return [UserRead.from_orm(user) for user in users]


def assign_role_to_user_fn(
    uow: AbstractUnitOfWork, user_id: int, role_id: int
) -> UserRead:
    with uow:
        user = uow.users.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        role = uow.roles.get(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        if role not in user.roles:
            user.roles.append(role)
        else:
            raise HTTPException(status_code=400, detail="Role already assigned to user")
    return UserRead.from_orm(user)


# Factory de servicios
def create_user_service() -> Dict[str, Callable]:
    return {
        UserService.CREATE: create_user_fn,
        UserService.READ: get_user_fn,
        UserService.ASSIGN_ROLE: assign_role_to_user_fn,
        UserService.UPDATE: update_user_fn,
        UserService.DELETE: delete_user_fn,
        UserService.LIST: list_users_fn,
    }
