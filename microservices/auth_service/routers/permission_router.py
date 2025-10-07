# routers/permission_router.py
from fastapi import APIRouter, Depends, status
from dependencies import get_permission_service, get_uow
from repositories.unit_of_work import AbstractUnitOfWork
from models.schemas import PermissionCreate, PermissionRead
from services.permission_service import PermissionService

permission_router = APIRouter()


@permission_router.post(
    "/permissions", response_model=PermissionRead, status_code=status.HTTP_201_CREATED
)
def create_permission(
    permission_data: PermissionCreate,
    uow: AbstractUnitOfWork = Depends(get_uow),
    service=Depends(get_permission_service),
):
    return service[PermissionService.CREATE](uow, permission_data)


@permission_router.get("/permissions/{perm_id}", response_model=PermissionRead)
def get_permission(
    perm_id: int,
    uow: AbstractUnitOfWork = Depends(get_uow),
    service=Depends(get_permission_service),
):
    return service[PermissionService.READ](uow, perm_id)


@permission_router.get("/permissions", response_model=list[PermissionRead])
def list_permissions(
    uow: AbstractUnitOfWork = Depends(get_uow),
    service=Depends(get_permission_service),
):
    return service[PermissionService.LIST](uow)


@permission_router.delete("/permissions/{perm_id}", response_model=PermissionRead)
def delete_permission(
    perm_id: int,
    uow: AbstractUnitOfWork = Depends(get_uow),
    service=Depends(get_permission_service),
):
    return service[PermissionService.DELETE](uow, perm_id)
