# models/entities.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Index
from sqlalchemy.sql import func
from database import Base

class Configuration(Base):
    __tablename__ = "app_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(255), nullable=False)
    config_value = Column(Text, nullable=False)
    environment = Column(String(50), nullable=False, default="development")
    service_name = Column(String(100), nullable=False, default="global")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Índice único compuesto
    __table_args__ = (
        Index('idx_unique_config', 'config_key', 'environment', 'service_name', unique=True),
    )

class FeatureFlag(Base):
    __tablename__ = "feature_flags"
    
    id = Column(Integer, primary_key=True, index=True)
    flag_name = Column(String(255), nullable=False)
    flag_key = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_enabled = Column(Boolean, default=True)
    rollout_percentage = Column(Integer, default=100)
    environment = Column(String(50), nullable=False, default="development")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_unique_flag', 'flag_key', 'environment', unique=True),
    )