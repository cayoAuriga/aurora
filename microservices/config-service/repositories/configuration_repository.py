"""
Configuration repository for database operations
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.configuration import AppConfiguration, ConfigHistory, ActionType, EnvironmentType
from ..schemas.configuration import ConfigurationCreate, ConfigurationUpdate


class ConfigurationRepository:
    """Repository for configuration operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, config_data: ConfigurationCreate) -> AppConfiguration:
        """Create a new configuration"""
        # Check if configuration already exists
        existing = self.get_by_key(
            config_data.config_key,
            config_data.environment,
            config_data.service_name
        )
        if existing:
            raise ValueError(f"Configuration already exists: {config_data.config_key}")
        
        db_config = AppConfiguration(**config_data.dict())
        self.db.add(db_config)
        self.db.flush()  # Get the ID
        
        # Create history record
        self._create_history_record(
            config_id=db_config.id,
            action=ActionType.CREATED,
            new_value=config_data.config_value,
            changed_by=config_data.created_by
        )
        
        self.db.commit()
        self.db.refresh(db_config)
        return db_config
    
    def get_by_id(self, config_id: int) -> Optional[AppConfiguration]:
        """Get configuration by ID"""
        return self.db.query(AppConfiguration).filter(
            AppConfiguration.id == config_id
        ).first()
    
    def get_by_key(
        self,
        config_key: str,
        environment: EnvironmentType = EnvironmentType.ALL,
        service_name: Optional[str] = None
    ) -> Optional[AppConfiguration]:
        """Get configuration by key, environment, and service"""
        query = self.db.query(AppConfiguration).filter(
            and_(
                AppConfiguration.config_key == config_key,
                AppConfiguration.environment == environment,
                AppConfiguration.service_name == service_name,
                AppConfiguration.is_active == True
            )
        )
        return query.first()
    
    def get_configurations(
        self,
        environment: Optional[EnvironmentType] = None,
        service_name: Optional[str] = None,
        is_active: bool = True,
        include_sensitive: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[AppConfiguration]:
        """Get configurations with filters"""
        query = self.db.query(AppConfiguration)
        
        # Apply filters
        filters = [AppConfiguration.is_active == is_active]
        
        if environment:
            filters.append(
                or_(
                    AppConfiguration.environment == environment,
                    AppConfiguration.environment == EnvironmentType.ALL
                )
            )
        
        if service_name is not None:
            filters.append(AppConfiguration.service_name == service_name)
        
        if not include_sensitive:
            filters.append(AppConfiguration.is_sensitive == False)
        
        query = query.filter(and_(*filters))
        
        return query.offset(skip).limit(limit).all()
    
    def get_configurations_as_dict(
        self,
        environment: Optional[EnvironmentType] = None,
        service_name: Optional[str] = None,
        include_sensitive: bool = False
    ) -> Dict[str, Any]:
        """Get configurations as a key-value dictionary"""
        configs = self.get_configurations(
            environment=environment,
            service_name=service_name,
            is_active=True,
            include_sensitive=include_sensitive,
            limit=1000  # Get all configs
        )
        
        result = {}
        for config in configs:
            result[config.config_key] = config.config_value
        
        return result
    
    def update(
        self,
        config_id: int,
        config_data: ConfigurationUpdate,
        changed_by: Optional[int] = None
    ) -> Optional[AppConfiguration]:
        """Update configuration"""
        db_config = self.get_by_id(config_id)
        if not db_config:
            return None
        
        # Store old value for history
        old_value = db_config.config_value
        
        # Update fields
        update_data = config_data.dict(exclude_unset=True)
        change_reason = update_data.pop('change_reason', None)
        
        for field, value in update_data.items():
            setattr(db_config, field, value)
        
        # Increment version
        db_config.version += 1
        
        self.db.flush()
        
        # Create history record
        self._create_history_record(
            config_id=db_config.id,
            action=ActionType.UPDATED,
            old_value=old_value,
            new_value=db_config.config_value,
            changed_by=changed_by,
            change_reason=change_reason
        )
        
        self.db.commit()
        self.db.refresh(db_config)
        return db_config
    
    def delete(self, config_id: int, changed_by: Optional[int] = None) -> bool:
        """Delete configuration (soft delete by setting is_active=False)"""
        db_config = self.get_by_id(config_id)
        if not db_config:
            return False
        
        # Store old value for history
        old_value = db_config.config_value
        
        # Soft delete
        db_config.is_active = False
        
        self.db.flush()
        
        # Create history record
        self._create_history_record(
            config_id=db_config.id,
            action=ActionType.DELETED,
            old_value=old_value,
            changed_by=changed_by
        )
        
        self.db.commit()
        return True
    
    def get_history(self, config_id: int, limit: int = 50) -> List[ConfigHistory]:
        """Get configuration change history"""
        return self.db.query(ConfigHistory).filter(
            ConfigHistory.config_id == config_id
        ).order_by(ConfigHistory.created_at.desc()).limit(limit).all()
    
    def _create_history_record(
        self,
        config_id: int,
        action: ActionType,
        old_value: Any = None,
        new_value: Any = None,
        changed_by: Optional[int] = None,
        change_reason: Optional[str] = None
    ):
        """Create a history record for configuration changes"""
        history = ConfigHistory(
            config_id=config_id,
            action=action,
            old_value=old_value,
            new_value=new_value,
            changed_by=changed_by,
            change_reason=change_reason
        )
        self.db.add(history)
    
    def count_configurations(
        self,
        environment: Optional[EnvironmentType] = None,
        service_name: Optional[str] = None,
        is_active: bool = True
    ) -> int:
        """Count configurations with filters"""
        query = self.db.query(AppConfiguration)
        
        filters = [AppConfiguration.is_active == is_active]
        
        if environment:
            filters.append(
                or_(
                    AppConfiguration.environment == environment,
                    AppConfiguration.environment == EnvironmentType.ALL
                )
            )
        
        if service_name is not None:
            filters.append(AppConfiguration.service_name == service_name)
        
        return query.filter(and_(*filters)).count()