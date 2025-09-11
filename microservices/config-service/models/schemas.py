"""
Pydantic schemas for the config-service
"""
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class ConfigurationCreate(BaseModel):
    """Schema for creating a new configuration"""
    config_key: str
    config_value: str
    environment: str = "development"
    service_name: str = "global"
    description: Optional[str] = None

class ConfigurationUpdate(BaseModel):
    """Schema for updating a configuration"""
    config_value: Optional[str] = None
    description: Optional[str] = None

class ConfigurationResponse(BaseModel):
    """Schema for configuration response"""
    id: int
    config_key: str
    config_value: str
    environment: str
    service_name: Optional[str] = "global"
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # 👇 validador para reemplazar None por "global"
    @field_validator("service_name", mode="before")
    @classmethod
    def default_service_name(cls, v):
        return v or "global"

    class Config:
        from_attributes = True

class FeatureFlagCreate(BaseModel):
    """Schema for creating a new feature flag"""
    flag_name: str
    flag_key: str
    description: Optional[str] = None
    is_enabled: bool = True
    rollout_percentage: int = 100
    environment: str = "development"

class FeatureFlagResponse(BaseModel):
    """Schema for feature flag response"""
    id: int
    flag_name: str
    flag_key: str
    description: Optional[str] = None
    is_enabled: bool
    rollout_percentage: int
    environment: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True