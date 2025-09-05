"""
Configuration models for the Configuration Service
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class EnvironmentType(enum.Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ALL = "all"


class ActionType(enum.Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"


class AppConfiguration(Base):
    """Application configuration model"""
    __tablename__ = "app_configurations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(100), nullable=False)
    config_value = Column(JSON, nullable=False)
    environment = Column(Enum(EnvironmentType), default=EnvironmentType.ALL)
    service_name = Column(String(50), nullable=True)  # NULL means global config
    description = Column(Text, nullable=True)
    is_sensitive = Column(Boolean, default=False)  # For secrets/passwords
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)  # User ID who created the config
    
    # Relationships
    history = relationship("ConfigHistory", back_populates="configuration", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AppConfiguration(key='{self.config_key}', env='{self.environment}', service='{self.service_name}')>"


class ConfigHistory(Base):
    """Configuration change history model"""
    __tablename__ = "config_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    config_id = Column(Integer, ForeignKey("app_configurations.id", ondelete="CASCADE"), nullable=False)
    action = Column(Enum(ActionType), nullable=False)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    changed_by = Column(Integer, nullable=True)
    change_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    configuration = relationship("AppConfiguration", back_populates="history")
    
    def __repr__(self):
        return f"<ConfigHistory(config_id={self.config_id}, action='{self.action}', created_at='{self.created_at}')>"