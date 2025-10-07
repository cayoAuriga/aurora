from repositories.unit_of_work import AbstractUnitOfWork
from fastapi import HTTPException, status
from models.schemas import RoleCreate, RoleUpdate, RoleRead
from typing import List, Callable, Dict
from enum import Enum

class RoleService(str, Enum):
    CREATE = "create_role"
    READ = "get_role",
    LIST = "get_all_roles",
    UPDATE = "update_role",
    DELETE = "delete_role"    
    ASSIGN_PERMISSION = "assign_permission_to_role"
    REVOKE_PERMISSION = "revoke_permission_from_role"
    ASSIGN_MANY_PERMISSIONS = "assign_many_permissions_to_role"

def assign_permission_to_role_fn(
    uow: AbstractUnitOfWork, role_id: int, perm_id: int
) -> RoleRead:
    with uow:
        role = uow.roles.get(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )
        perm = uow.permissions.get(perm_id)
        if not perm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found"
            )
        updated_role = uow.roles.assign_permission(role, perm)
    return RoleRead.from_orm(updated_role)


def create_role_fn(uow: AbstractUnitOfWork, data: RoleCreate) -> RoleRead:
    with uow:
        role = uow.roles.get_by_name(data.name)
        if role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Role already exists"
            )
        role = uow.roles.create(data)
    return RoleRead.from_orm(role)

def get_role_fn(uow: AbstractUnitOfWork, role_id: int) -> RoleRead:
    with uow:
        role = uow.roles.get(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )
    return RoleRead.from_orm(role)

def update_role_fn(uow: AbstractUnitOfWork, role_id: int, data: RoleUpdate) -> RoleRead:
    with uow:
        role = uow.roles.get(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )
        if data.name:
            existing_role = uow.roles.get_by_name(data.name)
            if existing_role and existing_role.id != role_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Role name already in use"
                )
            role.name = data.name
        updated_role = uow.roles.update(role)
    return RoleRead.from_orm(updated_role)

def list_roles_fn(uow: AbstractUnitOfWork) -> List[RoleRead]:
    with uow:
        roles = uow.roles.get_all()
    return [RoleRead.from_orm(role) for role in roles]

def revoke_permission_from_role_fn(
    uow: AbstractUnitOfWork, role_id: int, perm_id: int
) -> RoleRead:
    with uow:
        role = uow.roles.get(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )
        perm = uow.permissions.get(perm_id)
        if not perm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found"
            )
        updated_role = uow.roles.revoke_permission(role, perm)
    return RoleRead.from_orm(updated_role)




def assign_many_permissions_to_role_fn(
    uow: AbstractUnitOfWork, role_id: int, perm_names: List[str]
) -> RoleRead:
    with uow:
        role = uow.roles.get(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )
        perms = uow.permissions.get_many_by_names(perm_names)
        if not all(perms):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more permissions not found",
            )
        updated_role = uow.roles.update_role_permissions(role, perms)
    return RoleRead.from_orm(updated_role)

def delete_role_fn(uow: AbstractUnitOfWork, role_id: int) -> bool:
    with uow:
        role = uow.roles.get(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )
        uow.roles.delete(role)
    return True

def create_role_service() -> Dict[str, Callable]:
    return {
        RoleService.CREATE: create_role_fn,
        RoleService.READ: get_role_fn,
        RoleService.DELETE: delete_role_fn,
        RoleService.UPDATE: update_role_fn,
        RoleService.LIST: list_roles_fn,
        RoleService.ASSIGN_MANY_PERMISSIONS: assign_many_permissions_to_role_fn,
        RoleService.ASSIGN_PERMISSION: assign_permission_to_role_fn,
        RoleService.REVOKE_PERMISSION: revoke_permission_from_role_fn,
    }
