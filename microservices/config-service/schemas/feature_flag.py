"""
Feature flag schemas for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Any, Dict
from datetime import datetime
from enum import Enum


class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ALL = "all"


class FeatureFlagBase(BaseModel):
    flag_name: str = Field(..., min_length=1, max_length=100, description="Human-readable flag name")
    flag_key: str = Field(..., min_length=1, max_length=100, description="Unique flag key")
    description: Optional[str] = Field(None, description="Flag description")
    is_enabled: bool = Field(default=False, description="Whether the flag is enabled")
    environment: EnvironmentType = Field(default=EnvironmentType.ALL, description="Target environment")
    service_name: Optional[str] = Field(None, max_length=50, description="Target service (null for global)")
    rollout_percentage: int = Field(default=0, ge=0, le=100, description="Rollout percentage (0-100)")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Complex conditions for flag activation")
    expires_at: Optional[datetime] = Field(None, description="Flag expiration date")


class FeatureFlagCreate(FeatureFlagBase):
    created_by: Optional[int] = Field(None, description="User ID who created the flag")
    
    @validator('flag_key')
    def validate_flag_key(cls, v):
        if not v or not v.strip():
            raise ValueError('Flag key cannot be empty')
        # Ensure key follows naming convention (snake_case)
        if not all(c.isalnum() or c == '_' for c in v):
            raise ValueError('Flag key can only contain alphanumeric characters and underscores')
        if not v.islower():
            raise ValueError('Flag key must be lowercase')
        return v.strip()
    
    @validator('rollout_percentage')
    def validate_rollout_percentage(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Rollout percentage must be between 0 and 100')
        return v


class FeatureFlagUpdate(BaseModel):
    flag_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None)
    is_enabled: Optional[bool] = Field(None)
    rollout_percentage: Optional[int] = Field(None, ge=0, le=100)
    conditions: Optional[Dict[str, Any]] = Field(None)
    expires_at: Optional[datetime] = Field(None)
    
    @validator('rollout_percentage')
    def validate_rollout_percentage(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Rollout percentage must be between 0 and 100')
        return v


class FeatureFlagResponse(FeatureFlagBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]
    
    class Config:
        from_attributes = True


class FeatureFlagEvaluation(BaseModel):
    """Response for feature flag evaluation"""
    flag_key: str
    is_enabled: bool
    rollout_percentage: int
    user_qualified: bool = Field(..., description="Whether the user qualifies for this flag")
    reason: str = Field(..., description="Reason for the evaluation result")
    expires_at: Optional[datetime] = None


class FeatureFlagQuery(BaseModel):
    """Query parameters for feature flag lookup"""
    environment: Optional[EnvironmentType] = None
    service_name: Optional[str] = None
    is_enabled: Optional[bool] = None
    include_expired: bool = Field(default=False, description="Include expired flags")


class BulkFeatureFlagResponse(BaseModel):
    """Response for bulk feature flag queries"""
    flags: Dict[str, bool] = Field(..., description="Key-value pairs of flag evaluations")
    total_count: int = Field(..., description="Total number of flags")
    environment: str = Field(..., description="Environment filter applied")
    service_name: Optional[str] = Field(None, description="Service filter applied")
    user_id: Optional[int] = Field(None, description="User ID used for evaluation")