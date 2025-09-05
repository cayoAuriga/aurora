"""
Feature flag API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..services.feature_flag_service import FeatureFlagService
from ..schemas.feature_flag import (
    FeatureFlagCreate,
    FeatureFlagUpdate,
    FeatureFlagResponse,
    FeatureFlagEvaluation,
    BulkFeatureFlagResponse,
    EnvironmentType
)
from shared.database import get_db_dependency
from shared.errors import NotFoundError, ValidationError

# Get database dependency
get_db = get_db_dependency("config-service")

router = APIRouter(prefix="/feature-flags", tags=["feature-flags"])


def get_feature_flag_service(db: Session = Depends(get_db)) -> FeatureFlagService:
    """Dependency to get feature flag service"""
    return FeatureFlagService(db)


@router.post("/", response_model=FeatureFlagResponse, status_code=201)
async def create_feature_flag(
    flag_data: FeatureFlagCreate,
    service: FeatureFlagService = Depends(get_feature_flag_service)
):
    """Create a new feature flag"""
    try:
        return service.create_feature_flag(flag_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[FeatureFlagResponse])
async def get_feature_flags(
    environment: Optional[EnvironmentType] = Query(None, description="Filter by environment"),
    service_name: Optional[str] = Query(None, description="Filter by service name"),
    is_enabled: Optional[bool] = Query(None, description="Filter by enabled status"),
    include_expired: bool = Query(False, description="Include expired flags"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    service: FeatureFlagService = Depends(get_feature_flag_service)
):
    """Get feature flags with optional filters"""
    return service.get_feature_flags(
        environment=environment,
        service_name=service_name,
        is_enabled=is_enabled,
        include_expired=include_expired,
        skip=skip,
        limit=limit
    )


@router.get("/bulk", response_model=BulkFeatureFlagResponse)
async def get_bulk_feature_flags(
    environment: Optional[EnvironmentType] = Query(None, description="Filter by environment"),
    service_name: Optional[str] = Query(None, description="Filter by service name"),
    user_id: Optional[int] = Query(None, description="User ID for flag evaluation"),
    service: FeatureFlagService = Depends(get_feature_flag_service)
):
    """Get feature flags as key-value pairs with evaluation"""
    return service.get_bulk_feature_flags(
        environment=environment,
        service_name=service_name,
        user_id=user_id
    )


@router.get("/{flag_id}", response_model=FeatureFlagResponse)
async def get_feature_flag(
    flag_id: int,
    service: FeatureFlagService = Depends(get_feature_flag_service)
):
    """Get feature flag by ID"""
    try:
        return service.get_feature_flag(flag_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/key/{flag_key}", response_model=Optional[FeatureFlagResponse])
async def get_feature_flag_by_key(
    flag_key: str,
    service: FeatureFlagService = Depends(get_feature_flag_service)
):
    """Get feature flag by key"""
    return service.get_feature_flag_by_key(flag_key)


@router.get("/evaluate/{flag_key}", response_model=FeatureFlagEvaluation)
async def evaluate_feature_flag(
    flag_key: str,
    user_id: Optional[int] = Query(None, description="User ID for evaluation"),
    environment: Optional[EnvironmentType] = Query(None, description="Environment filter"),
    service: FeatureFlagService = Depends(get_feature_flag_service)
):
    """Evaluate a feature flag for a specific user"""
    return service.evaluate_feature_flag(
        flag_key=flag_key,
        user_id=user_id,
        environment=environment
    )


@router.get("/check/{flag_key}")
async def check_feature_flag(
    flag_key: str,
    user_id: Optional[int] = Query(None, description="User ID for evaluation"),
    environment: Optional[EnvironmentType] = Query(None, description="Environment filter"),
    service: FeatureFlagService = Depends(get_feature_flag_service)
):
    """Simple boolean check if feature is enabled for user"""
    enabled = service.is_feature_enabled(
        flag_key=flag_key,
        user_id=user_id,
        environment=environment
    )
    return {"flag_key": flag_key, "enabled": enabled}


@router.put("/{flag_id}", response_model=FeatureFlagResponse)
async def update_feature_flag(
    flag_id: int,
    flag_data: FeatureFlagUpdate,
    service: FeatureFlagService = Depends(get_feature_flag_service)
):
    """Update feature flag"""
    try:
        return service.update_feature_flag(flag_id, flag_data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/toggle/{flag_key}", response_model=FeatureFlagResponse)
async def toggle_feature_flag(
    flag_key: str,
    enabled: bool = Query(..., description="Enable or disable the flag"),
    service: FeatureFlagService = Depends(get_feature_flag_service)
):
    """Toggle feature flag on/off"""
    try:
        return service.toggle_feature_flag(flag_key, enabled)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/rollout/{flag_key}", response_model=FeatureFlagResponse)
async def update_rollout_percentage(
    flag_key: str,
    percentage: int = Query(..., ge=0, le=100, description="Rollout percentage (0-100)"),
    service: FeatureFlagService = Depends(get_feature_flag_service)
):
    """Update rollout percentage for gradual rollout"""
    try:
        return service.update_rollout_percentage(flag_key, percentage)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{flag_id}")
async def delete_feature_flag(
    flag_id: int,
    service: FeatureFlagService = Depends(get_feature_flag_service)
):
    """Delete feature flag"""
    try:
        success = service.delete_feature_flag(flag_id)
        return {"success": success, "message": "Feature flag deleted successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))