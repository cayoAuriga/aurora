from repositories.unit_of_work import AbstractUnitOfWork
from fastapi import HTTPException, status
from models.schemas import PermissionCreate, PermissionRead
from typing import Callable, Dict
from enum import Enum

class PermissionService(str, Enum):
    CREATE = "create_permission"
    READ = "get_permission"
    LIST = "get_all_permissions"
    DELETE = "delete_permission"

def create_permission_fn(uow: AbstractUnitOfWork, data: PermissionCreate) -> PermissionRead:
    with uow:
        permission = uow.permissions.get_by_name(data.name)
        if permission:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Permission already exists")
        permission = uow.permissions.create(data)
        return permission

def get_permission_fn(uow: AbstractUnitOfWork, perm_id: int) -> PermissionRead:
    with uow:
        permission = uow.permissions.get(perm_id)
        if not permission:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
        return permission

def get_all_permissions_fn(uow: AbstractUnitOfWork) -> list[PermissionRead]:
    with uow:
        permissions = uow.permissions.get_all()
        return permissions

def delete_permission_fn(uow: AbstractUnitOfWork, perm_id: int) -> PermissionRead:
    with uow:
        permission = uow.permissions.get(perm_id)
        if not permission:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
        uow.permissions.delete(perm_id)
        return permission

def create_permission_service() -> Dict[str, Callable]:
    return {
        PermissionService.CREATE: create_permission_fn,
        PermissionService.READ: get_permission_fn,
        PermissionService.LIST: get_all_permissions_fn,
        PermissionService.DELETE: delete_permission_fn
    }