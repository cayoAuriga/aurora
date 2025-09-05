"""
Configuration schemas for request/response validation
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


class ActionType(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"


class ConfigurationBase(BaseModel):
    config_key: str = Field(..., min_length=1, max_length=100, description="Configuration key")
    config_value: Any = Field(..., description="Configuration value (can be any JSON-serializable type)")
    environment: EnvironmentType = Field(default=EnvironmentType.ALL, description="Target environment")
    service_name: Optional[str] = Field(None, max_length=50, description="Target service (null for global)")
    description: Optional[str] = Field(None, description="Configuration description")
    is_sensitive: bool = Field(default=False, description="Whether this config contains sensitive data")


class ConfigurationCreate(ConfigurationBase):
    created_by: Optional[int] = Field(None, description="User ID who created the config")
    
    @validator('config_key')
    def validate_config_key(cls, v):
        if not v or not v.strip():
            raise ValueError('Config key cannot be empty')
        # Ensure key follows naming convention
        if not all(c.isalnum() or c in '._-' for c in v):
            raise ValueError('Config key can only contain alphanumeric characters, dots, underscores, and hyphens')
        return v.strip()


class ConfigurationUpdate(BaseModel):
    config_value: Optional[Any] = Field(None, description="New configuration value")
    description: Optional[str] = Field(None, description="Updated description")
    is_sensitive: Optional[bool] = Field(None, description="Whether this config contains sensitive data")
    is_active: Optional[bool] = Field(None, description="Whether this config is active")
    change_reason: Optional[str] = Field(None, description="Reason for the change")


class ConfigurationResponse(ConfigurationBase):
    id: int
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]
    
    class Config:
        from_attributes = True


class ConfigHistoryResponse(BaseModel):
    id: int
    config_id: int
    action: ActionType
    old_value: Optional[Any]
    new_value: Optional[Any]
    changed_by: Optional[int]
    change_reason: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConfigurationQuery(BaseModel):
    """Query parameters for configuration lookup"""
    environment: Optional[EnvironmentType] = None
    service_name: Optional[str] = None
    is_active: Optional[bool] = True
    include_sensitive: bool = Field(default=False, description="Include sensitive configurations")


class BulkConfigurationResponse(BaseModel):
    """Response for bulk configuration queries"""
    configurations: Dict[str, Any] = Field(..., description="Key-value pairs of configurations")
    total_count: int = Field(..., description="Total number of configurations")
    environment: str = Field(..., description="Environment filter applied")
    service_name: Optional[str] = Field(None, description="Service filter applied")