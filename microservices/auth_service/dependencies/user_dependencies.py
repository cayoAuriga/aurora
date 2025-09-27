# dependencies/user_dependencies.py
from functools import lru_cache
from fastapi import Depends
from services.user_service import create_user_service
from services.decorators import with_error_handling, with_logging
from repositories.user_repository import UserRepository
from repositories.role_repository import RoleRepository
from repositories.permission_repository import PermissionRepository
from repositories.session_repository import SessionRepository

@lru_cache()
def get_user_repository() -> UserRepository:
    return UserRepository()

@lru_cache()
def get_role_repository() -> RoleRepository:
    return RoleRepository()

@lru_cache()
def get_permission_repository() -> PermissionRepository:
    return PermissionRepository()

@lru_cache()
def get_session_repository() -> SessionRepository:
    return SessionRepository(...)  # tu colección MongoDB

def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    role_repo: RoleRepository = Depends(get_role_repository),
    perm_repo: PermissionRepository = Depends(get_permission_repository),
    sess_repo: SessionRepository = Depends(get_session_repository)
):
    service = create_user_service(user_repo, role_repo, perm_repo, sess_repo)
    # pipeline de decorators
    for k in service.keys():
        service[k] = with_logging(with_error_handling(service[k]))
    return service
