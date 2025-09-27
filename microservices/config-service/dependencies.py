# dependencies.py

from functools import lru_cache, partial
from typing import Dict, Callable, Type, Any
from fastapi import Depends
from sqlalchemy.orm import Session


# === REPOSITORY FACTORY ===
def repository_factory(repo_cls: Type[Any]):
    """
    Factory for repositories (singleton with lru_cache)
    Example: get_configuration_repository = repository_factory(ConfigurationRepository)
    """
    @lru_cache()
    def get_repo() -> Any:
        return repo_cls()
    return get_repo


# === SERVICE FUNCTIONS FACTORY ===
def service_functions_factory(
    service_creator: Callable[[Any], Dict[str, Callable]],
    repository_dep: Callable = None
):
    """
    Factory that returns a dict of service functions with repository baked-in.
    Example:
        get_configuration_functions = service_functions_factory(create_configuration_service, get_configuration_repository)
    """
    def get_functions(repository: Any = Depends(repository_dep)) -> Dict[str, Callable]:
        return service_creator(repository)
    return get_functions


# === INDIVIDUAL FUNCTION FACTORY ===
def single_function_factory(
    fn: Callable,
    repository_dep: Callable
):
    """
    Factory for injecting a single function with repository baked-in.
    Example:
        get_create_configuration_fn = single_function_factory(create_configuration_fn, get_configuration_repository)
    """
    def get_fn(repository: Any = Depends(repository_dep)) -> Callable:
        return partial(fn, repository)
    return get_fn


# === ENHANCED SERVICE PIPELINE ===
def pipeline_factory(
    service_creator: Callable[[Any], Dict[str, Callable]],
    decorators: list[Callable[[Callable], Callable]],
    repository_dep: Callable
):
    """
    Factory that composes a pipeline of decorators (logging, error handling, etc.)
    Example:
        get_composed_configuration_service = pipeline_factory(
            create_configuration_service,
            [with_logging, with_error_handling],
            get_configuration_repository
        )
    """
    def get_pipeline(repository: Any = Depends(repository_dep)) -> Dict[str, Callable]:
        base_fns = service_creator(repository)
        enhanced = {}
        for name, fn in base_fns.items():
            # Compose decorators in order
            for deco in decorators:
                fn = deco(fn)
            enhanced[name] = fn
        return enhanced
    return get_pipeline