# dependencies.py (continuación)
from functools import partial, lru_cache
from fastapi import Depends

def repository_factory(repo_cls, *args, **kwargs):
    @lru_cache()
    def get_repo():
        return repo_cls(*args, **kwargs)
    return get_repo

def service_functions_factory(service_creator: Callable, repo_dep: Callable):
    """Factory que devuelve funciones con repo inyectado"""
    def get_functions(repo = Depends(repo_dep)):
        return service_creator(repo)
    return get_functions

# Factory para sesiones
def create_session_service(repo: SessionRepository):
    return {
        "create": partial(create_session_fn, repo),
        "get": partial(get_session_fn, repo),
        "delete": partial(delete_session_fn, repo),
        "invalidate_expired": partial(invalidate_expired_sessions_fn, repo)
    }
def create_auth_service(
    user_repo, 
    session_repo
):
    return {
        "exchange_google_code": partial(exchange_google_code_fn, user_repo, session_repo)
    }

# Dependencias
get_user_repository = repository_factory(UserRepository)
get_session_repository = repository_factory(SessionRepository, collection)
get_auth_service = service_functions_factory(
    create_auth_service,
    repo_dep=None  # los repos se pasan manualmente porque necesitamos dos
)
# User dependencies
get_user_repository = lambda: lru_cache()(UserRepository)()
get_role_repository = lambda: lru_cache()(RoleRepository)()
get_permission_repository = lambda: lru_cache()(PermissionRepository)()

def get_user_service():
    return create_user_service(
        user_repo=get_user_repository(),
        role_repo=get_role_repository(),
        perm_repo=get_permission_repository()
    )