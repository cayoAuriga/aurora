# routers/role_router.py
from fastapi import APIRouter, Depends, status
from dependencies import get_role_service, get_uow
from repositories.unit_of_work import AbstractUnitOfWork
from models.schemas import RoleCreate, RoleRead
from services.role_service import RoleService

role_router = APIRouter()


# --- ROLES ---
@role_router.post(
    "/roles", response_model=RoleRead, status_code=status.HTTP_201_CREATED
)
def create_role(
    role_data: RoleCreate,  # Usa el schema para validación automática
    uow: AbstractUnitOfWork = Depends(get_uow),
    service=Depends(get_role_service),
):
    return service[RoleService.CREATE](uow, role_data)


@role_router.get("/roles/{role_id}", response_model=RoleRead)
def get_role(
    role_id: int,
    uow: AbstractUnitOfWork = Depends(get_uow),
    service=Depends(get_role_service),
):
    return service[RoleService.READ](uow, role_id)

@role_router.get("/roles", response_model=list[RoleRead])
def get_all_roles(
    uow: AbstractUnitOfWork = Depends(get_uow),
    service=Depends(get_role_service),
):
    return service[RoleService.LIST](uow)

@role_router.put("/roles/{role_id}", response_model=RoleRead)
def update_role(
    role_id: int,
    role_data: RoleCreate,
    uow: AbstractUnitOfWork = Depends(get_uow),
    service=Depends(get_role_service),
):
    return service[RoleService.UPDATE](uow, role_id, role_data)

@role_router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    uow: AbstractUnitOfWork = Depends(get_uow),
    service=Depends(get_role_service),
):
    success = service[RoleService.DELETE](uow, role_id)
    if not success:
        return {"detail": "Role deletion failed"}
    return {"detail": "Role deleted successfully"}




@role_router.post("/roles/{role_id}/permissions/{perm_id}", response_model=RoleRead)
def assign_permission_to_role(
    role_id: int,
    perm_id: int,
    uow: AbstractUnitOfWork = Depends(get_uow),
    service=Depends(get_role_service),
):
    return service[RoleService.ASSIGN_PERMISSION](uow, role_id, perm_id)


@role_router.post("/roles/{role_id}/permissions/batch", response_model=RoleRead)
def assign_many_permissions_to_role(
    role_id: int,
    permissions: list[str],
    uow: AbstractUnitOfWork = Depends(get_uow),
    service=Depends(get_role_service),
):
    return service[RoleService.ASSIGN_MANY_PERMISSIONS](uow, role_id, permissions)


@role_router.post(
    "/roles/{role_id}/permissions/revoke/{perm_id}", response_model=RoleRead
)
def revoke_permission_from_role(
    role_id: int,
    perm_id: int,
    uow: AbstractUnitOfWork = Depends(get_uow),
    service=Depends(get_role_service),
):
    return service[RoleService.REVOKE_PERMISSION](uow, role_id, perm_id)
