"""
Feature flag models for the Configuration Service
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class EnvironmentType(enum.Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ALL = "all"


class FeatureFlag(Base):
    """Feature flag model"""
    __tablename__ = "feature_flags"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    flag_name = Column(String(100), nullable=False)
    flag_key = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_enabled = Column(Boolean, default=False)
    environment = Column(Enum(EnvironmentType), default=EnvironmentType.ALL)
    service_name = Column(String(50), nullable=True)  # NULL means global flag
    rollout_percentage = Column(Integer, default=0)  # 0-100 for gradual rollout
    conditions = Column(JSON, nullable=True)  # Complex conditions for flag activation
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<FeatureFlag(key='{self.flag_key}', enabled={self.is_enabled}, env='{self.environment}')>"
    
    def is_expired(self) -> bool:
        """Check if the feature flag has expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def should_be_enabled_for_user(self, user_id: int = None) -> bool:
        """
        Determine if the feature flag should be enabled for a specific user
        Based on rollout percentage and conditions
        """
        if not self.is_enabled or self.is_expired():
            return False
        
        # If rollout is 100%, enable for everyone
        if self.rollout_percentage >= 100:
            return True
        
        # If rollout is 0%, disable for everyone
        if self.rollout_percentage <= 0:
            return False
        
        # Use user_id for consistent rollout (same user always gets same result)
        if user_id is not None:
            # Simple hash-based rollout
            user_hash = hash(f"{self.flag_key}_{user_id}") % 100
            return user_hash < self.rollout_percentage
        
        # If no user_id provided, use random rollout
        import random
        return random.randint(0, 99) < self.rollout_percentage