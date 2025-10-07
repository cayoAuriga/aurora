# routers/user_router.py
from fastapi import APIRouter, Depends, status
from dependencies import get_user_service, get_uow
from repositories.unit_of_work import AbstractUnitOfWork
from models.schemas import UserCreate, UserRead,UserUpdate, RoleCreate, RoleRead # Usa los Schemas
from services.user_service import UserService
user_router = APIRouter()

# --- USERS ---
@user_router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate, # Usa el schema para validación automática
    uow: AbstractUnitOfWork = Depends(get_uow), 
    service = Depends(get_user_service)
):
    return service[UserService.CREATE](uow, user_data)


@user_router.get("/users/{user_id}", response_model=UserRead)
def get_user(
    user_id: int, 
    uow: AbstractUnitOfWork = Depends(get_uow), 
    service=Depends(get_user_service)
):    
    return service[UserService.READ](uow, user_id)

@user_router.put("/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: int, 
    user_data: UserUpdate, # Usa el schema para validación automática
    uow: AbstractUnitOfWork = Depends(get_uow), 
    service=Depends(get_user_service)
):
    return service[UserService.UPDATE](uow, user_id, user_data)

@user_router.delete("/users/{user_id}", response_model=UserRead)
def delete_user(
    user_id: int, 
    uow: AbstractUnitOfWork = Depends(get_uow), 
    service=Depends(get_user_service)
):    
    return service[UserService.DELETE](uow, user_id)    

@user_router.get("/users", response_model=list[UserRead])
def list_users(
    uow: AbstractUnitOfWork = Depends(get_uow), 
    service=Depends(get_user_service)
):
    return service[UserService.LIST](uow)

@user_router.post("/users/{user_id}/[role_id]", response_model=UserRead)
def assign_role_to_user(
    user_id: int,
    role_id: int,
    uow: AbstractUnitOfWork = Depends(get_uow),
    service=Depends(get_user_service)
):
    return service[UserService.ASSIGN_ROLE](uow, user_id, role_id)