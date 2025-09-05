"""
Configuration API endpoints
"""
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..services.configuration_service import ConfigurationService
from ..schemas.configuration import (
    ConfigurationCreate,
    ConfigurationUpdate,
    ConfigurationResponse,
    ConfigHistoryResponse,
    BulkConfigurationResponse,
    EnvironmentType
)
from shared.database import get_db_dependency
from shared.errors import NotFoundError, ValidationError

# Get database dependency
get_db = get_db_dependency("config-service")

router = APIRouter(prefix="/configurations", tags=["configurations"])


def get_configuration_service(db: Session = Depends(get_db)) -> ConfigurationService:
    """Dependency to get configuration service"""
    return ConfigurationService(db)


@router.post("/", response_model=ConfigurationResponse, status_code=201)
async def create_configuration(
    config_data: ConfigurationCreate,
    service: ConfigurationService = Depends(get_configuration_service)
):
    """Create a new configuration"""
    try:
        return service.create_configuration(config_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ConfigurationResponse])
async def get_configurations(
    environment: Optional[EnvironmentType] = Query(None, description="Filter by environment"),
    service_name: Optional[str] = Query(None, description="Filter by service name"),
    is_active: bool = Query(True, description="Filter by active status"),
    include_sensitive: bool = Query(False, description="Include sensitive configurations"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    service: ConfigurationService = Depends(get_configuration_service)
):
    """Get configurations with optional filters"""
    return service.get_configurations(
        environment=environment,
        service_name=service_name,
        is_active=is_active,
        include_sensitive=include_sensitive,
        skip=skip,
        limit=limit
    )


@router.get("/bulk", response_model=BulkConfigurationResponse)
async def get_bulk_configurations(
    environment: Optional[EnvironmentType] = Query(None, description="Filter by environment"),
    service_name: Optional[str] = Query(None, description="Filter by service name"),
    include_sensitive: bool = Query(False, description="Include sensitive configurations"),
    service: ConfigurationService = Depends(get_configuration_service)
):
    """Get configurations as key-value pairs"""
    return service.get_bulk_configurations(
        environment=environment,
        service_name=service_name,
        include_sensitive=include_sensitive
    )


@router.get("/{config_id}", response_model=ConfigurationResponse)
async def get_configuration(
    config_id: int,
    service: ConfigurationService = Depends(get_configuration_service)
):
    """Get configuration by ID"""
    try:
        return service.get_configuration(config_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/key/{config_key}", response_model=Optional[ConfigurationResponse])
async def get_configuration_by_key(
    config_key: str,
    environment: EnvironmentType = Query(EnvironmentType.ALL, description="Environment filter"),
    service_name: Optional[str] = Query(None, description="Service name filter"),
    service: ConfigurationService = Depends(get_configuration_service)
):
    """Get configuration by key"""
    return service.get_configuration_by_key(
        config_key=config_key,
        environment=environment,
        service_name=service_name
    )


@router.get("/value/{config_key}")
async def get_configuration_value(
    config_key: str,
    environment: EnvironmentType = Query(EnvironmentType.ALL, description="Environment filter"),
    service_name: Optional[str] = Query(None, description="Service name filter"),
    default_value: Optional[str] = Query(None, description="Default value if not found"),
    service: ConfigurationService = Depends(get_configuration_service)
):
    """Get configuration value directly"""
    value = service.get_configuration_value(
        config_key=config_key,
        environment=environment,
        service_name=service_name,
        default_value=default_value
    )
    return {"key": config_key, "value": value}


@router.put("/{config_id}", response_model=ConfigurationResponse)
async def update_configuration(
    config_id: int,
    config_data: ConfigurationUpdate,
    changed_by: Optional[int] = Query(None, description="User ID making the change"),
    service: ConfigurationService = Depends(get_configuration_service)
):
    """Update configuration"""
    try:
        return service.update_configuration(config_id, config_data, changed_by)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/key/{config_key}", response_model=ConfigurationResponse)
async def set_configuration_value(
    config_key: str,
    config_value: Any,
    environment: EnvironmentType = Query(EnvironmentType.ALL, description="Environment"),
    service_name: Optional[str] = Query(None, description="Service name"),
    description: Optional[str] = Query(None, description="Configuration description"),
    is_sensitive: bool = Query(False, description="Is sensitive configuration"),
    changed_by: Optional[int] = Query(None, description="User ID making the change"),
    service: ConfigurationService = Depends(get_configuration_service)
):
    """Set configuration value (create or update)"""
    try:
        return service.set_configuration_value(
            config_key=config_key,
            config_value=config_value,
            environment=environment,
            service_name=service_name,
            description=description,
            is_sensitive=is_sensitive,
            changed_by=changed_by
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{config_id}")
async def delete_configuration(
    config_id: int,
    changed_by: Optional[int] = Query(None, description="User ID making the change"),
    service: ConfigurationService = Depends(get_configuration_service)
):
    """Delete configuration"""
    try:
        success = service.delete_configuration(config_id, changed_by)
        return {"success": success, "message": "Configuration deleted successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{config_id}/history", response_model=List[ConfigHistoryResponse])
async def get_configuration_history(
    config_id: int,
    limit: int = Query(50, ge=1, le=200, description="Maximum number of history records"),
    service: ConfigurationService = Depends(get_configuration_service)
):
    """Get configuration change history"""
    try:
        return service.get_configuration_history(config_id, limit)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))