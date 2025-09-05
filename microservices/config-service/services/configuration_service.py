"""
Configuration service business logic
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from ..repositories.configuration_repository import ConfigurationRepository
from ..schemas.configuration import (
    ConfigurationCreate,
    ConfigurationUpdate,
    ConfigurationResponse,
    ConfigHistoryResponse,
    BulkConfigurationResponse,
    EnvironmentType
)
from ..models.configuration import AppConfiguration, ConfigHistory
from shared.errors import NotFoundError, ValidationError


class ConfigurationService:
    """Business logic for configuration management"""
    
    def __init__(self, db: Session):
        self.repository = ConfigurationRepository(db)
    
    def create_configuration(
        self,
        config_data: ConfigurationCreate
    ) -> ConfigurationResponse:
        """Create a new configuration"""
        try:
            config = self.repository.create(config_data)
            return ConfigurationResponse.from_orm(config)
        except ValueError as e:
            raise ValidationError(str(e))
    
    def get_configuration(self, config_id: int) -> ConfigurationResponse:
        """Get configuration by ID"""
        config = self.repository.get_by_id(config_id)
        if not config:
            raise NotFoundError("Configuration", str(config_id))
        
        return ConfigurationResponse.from_orm(config)
    
    def get_configuration_by_key(
        self,
        config_key: str,
        environment: EnvironmentType = EnvironmentType.ALL,
        service_name: Optional[str] = None
    ) -> Optional[ConfigurationResponse]:
        """Get configuration by key"""
        config = self.repository.get_by_key(config_key, environment, service_name)
        if not config:
            return None
        
        return ConfigurationResponse.from_orm(config)
    
    def get_configurations(
        self,
        environment: Optional[EnvironmentType] = None,
        service_name: Optional[str] = None,
        is_active: bool = True,
        include_sensitive: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[ConfigurationResponse]:
        """Get configurations with filters"""
        configs = self.repository.get_configurations(
            environment=environment,
            service_name=service_name,
            is_active=is_active,
            include_sensitive=include_sensitive,
            skip=skip,
            limit=limit
        )
        
        return [ConfigurationResponse.from_orm(config) for config in configs]
    
    def get_bulk_configurations(
        self,
        environment: Optional[EnvironmentType] = None,
        service_name: Optional[str] = None,
        include_sensitive: bool = False
    ) -> BulkConfigurationResponse:
        """Get configurations as key-value pairs"""
        configs_dict = self.repository.get_configurations_as_dict(
            environment=environment,
            service_name=service_name,
            include_sensitive=include_sensitive
        )
        
        total_count = self.repository.count_configurations(
            environment=environment,
            service_name=service_name,
            is_active=True
        )
        
        return BulkConfigurationResponse(
            configurations=configs_dict,
            total_count=total_count,
            environment=environment.value if environment else "all",
            service_name=service_name
        )
    
    def update_configuration(
        self,
        config_id: int,
        config_data: ConfigurationUpdate,
        changed_by: Optional[int] = None
    ) -> ConfigurationResponse:
        """Update configuration"""
        config = self.repository.update(config_id, config_data, changed_by)
        if not config:
            raise NotFoundError("Configuration", str(config_id))
        
        return ConfigurationResponse.from_orm(config)
    
    def delete_configuration(
        self,
        config_id: int,
        changed_by: Optional[int] = None
    ) -> bool:
        """Delete configuration"""
        success = self.repository.delete(config_id, changed_by)
        if not success:
            raise NotFoundError("Configuration", str(config_id))
        
        return success
    
    def get_configuration_history(
        self,
        config_id: int,
        limit: int = 50
    ) -> List[ConfigHistoryResponse]:
        """Get configuration change history"""
        # Verify configuration exists
        config = self.repository.get_by_id(config_id)
        if not config:
            raise NotFoundError("Configuration", str(config_id))
        
        history = self.repository.get_history(config_id, limit)
        return [ConfigHistoryResponse.from_orm(record) for record in history]
    
    def get_configuration_value(
        self,
        config_key: str,
        environment: EnvironmentType = EnvironmentType.ALL,
        service_name: Optional[str] = None,
        default_value: Any = None
    ) -> Any:
        """Get configuration value directly"""
        config = self.repository.get_by_key(config_key, environment, service_name)
        if not config:
            return default_value
        
        return config.config_value
    
    def set_configuration_value(
        self,
        config_key: str,
        config_value: Any,
        environment: EnvironmentType = EnvironmentType.ALL,
        service_name: Optional[str] = None,
        description: Optional[str] = None,
        is_sensitive: bool = False,
        changed_by: Optional[int] = None
    ) -> ConfigurationResponse:
        """Set configuration value (create or update)"""
        existing_config = self.repository.get_by_key(config_key, environment, service_name)
        
        if existing_config:
            # Update existing configuration
            update_data = ConfigurationUpdate(
                config_value=config_value,
                description=description,
                is_sensitive=is_sensitive
            )
            return self.update_configuration(existing_config.id, update_data, changed_by)
        else:
            # Create new configuration
            create_data = ConfigurationCreate(
                config_key=config_key,
                config_value=config_value,
                environment=environment,
                service_name=service_name,
                description=description,
                is_sensitive=is_sensitive,
                created_by=changed_by
            )
            return self.create_configuration(create_data)