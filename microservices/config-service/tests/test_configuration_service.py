"""
Unit tests for Configuration Service
"""
import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from ..services.configuration_service import ConfigurationService
from ..schemas.configuration import ConfigurationCreate, ConfigurationUpdate, EnvironmentType
from ..models.configuration import AppConfiguration
from shared.errors import NotFoundError, ValidationError


class TestConfigurationService:
    """Test cases for ConfigurationService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = Mock(spec=Session)
        self.service = ConfigurationService(self.mock_db)
        self.mock_repository = Mock()
        self.service.repository = self.mock_repository
    
    def test_create_configuration_success(self):
        """Test successful configuration creation"""
        # Arrange
        config_data = ConfigurationCreate(
            config_key="test.key",
            config_value="test_value",
            environment=EnvironmentType.DEVELOPMENT,
            description="Test configuration"
        )
        
        mock_config = AppConfiguration(
            id=1,
            config_key="test.key",
            config_value="test_value",
            environment=EnvironmentType.DEVELOPMENT,
            description="Test configuration",
            version=1,
            is_active=True
        )
        
        self.mock_repository.create.return_value = mock_config
        
        # Act
        result = self.service.create_configuration(config_data)
        
        # Assert
        self.mock_repository.create.assert_called_once_with(config_data)
        assert result.config_key == "test.key"
        assert result.config_value == "test_value"
    
    def test_create_configuration_duplicate_key(self):
        """Test configuration creation with duplicate key"""
        # Arrange
        config_data = ConfigurationCreate(
            config_key="duplicate.key",
            config_value="test_value"
        )
        
        self.mock_repository.create.side_effect = ValueError("Configuration already exists")
        
        # Act & Assert
        with pytest.raises(ValidationError):
            self.service.create_configuration(config_data)
    
    def test_get_configuration_success(self):
        """Test successful configuration retrieval"""
        # Arrange
        config_id = 1
        mock_config = AppConfiguration(
            id=config_id,
            config_key="test.key",
            config_value="test_value"
        )
        
        self.mock_repository.get_by_id.return_value = mock_config
        
        # Act
        result = self.service.get_configuration(config_id)
        
        # Assert
        self.mock_repository.get_by_id.assert_called_once_with(config_id)
        assert result.id == config_id
        assert result.config_key == "test.key"
    
    def test_get_configuration_not_found(self):
        """Test configuration retrieval when not found"""
        # Arrange
        config_id = 999
        self.mock_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(NotFoundError):
            self.service.get_configuration(config_id)
    
    def test_update_configuration_success(self):
        """Test successful configuration update"""
        # Arrange
        config_id = 1
        update_data = ConfigurationUpdate(
            config_value="updated_value",
            description="Updated description"
        )
        
        mock_config = AppConfiguration(
            id=config_id,
            config_key="test.key",
            config_value="updated_value",
            description="Updated description",
            version=2
        )
        
        self.mock_repository.update.return_value = mock_config
        
        # Act
        result = self.service.update_configuration(config_id, update_data)
        
        # Assert
        self.mock_repository.update.assert_called_once_with(config_id, update_data, None)
        assert result.config_value == "updated_value"
        assert result.version == 2
    
    def test_update_configuration_not_found(self):
        """Test configuration update when not found"""
        # Arrange
        config_id = 999
        update_data = ConfigurationUpdate(config_value="new_value")
        
        self.mock_repository.update.return_value = None
        
        # Act & Assert
        with pytest.raises(NotFoundError):
            self.service.update_configuration(config_id, update_data)
    
    def test_delete_configuration_success(self):
        """Test successful configuration deletion"""
        # Arrange
        config_id = 1
        self.mock_repository.delete.return_value = True
        
        # Act
        result = self.service.delete_configuration(config_id)
        
        # Assert
        self.mock_repository.delete.assert_called_once_with(config_id, None)
        assert result is True
    
    def test_delete_configuration_not_found(self):
        """Test configuration deletion when not found"""
        # Arrange
        config_id = 999
        self.mock_repository.delete.return_value = False
        
        # Act & Assert
        with pytest.raises(NotFoundError):
            self.service.delete_configuration(config_id)
    
    def test_get_configuration_value_exists(self):
        """Test getting configuration value when it exists"""
        # Arrange
        config_key = "test.key"
        mock_config = AppConfiguration(
            config_key=config_key,
            config_value="test_value"
        )
        
        self.mock_repository.get_by_key.return_value = mock_config
        
        # Act
        result = self.service.get_configuration_value(config_key)
        
        # Assert
        assert result == "test_value"
    
    def test_get_configuration_value_not_exists(self):
        """Test getting configuration value when it doesn't exist"""
        # Arrange
        config_key = "nonexistent.key"
        default_value = "default"
        
        self.mock_repository.get_by_key.return_value = None
        
        # Act
        result = self.service.get_configuration_value(config_key, default_value=default_value)
        
        # Assert
        assert result == default_value
    
    def test_set_configuration_value_new(self):
        """Test setting configuration value for new key"""
        # Arrange
        config_key = "new.key"
        config_value = "new_value"
        
        self.mock_repository.get_by_key.return_value = None
        
        mock_config = AppConfiguration(
            id=1,
            config_key=config_key,
            config_value=config_value
        )
        
        self.mock_repository.create.return_value = mock_config
        
        # Act
        result = self.service.set_configuration_value(config_key, config_value)
        
        # Assert
        self.mock_repository.create.assert_called_once()
        assert result.config_key == config_key
        assert result.config_value == config_value
    
    def test_set_configuration_value_existing(self):
        """Test setting configuration value for existing key"""
        # Arrange
        config_key = "existing.key"
        config_value = "updated_value"
        
        existing_config = AppConfiguration(
            id=1,
            config_key=config_key,
            config_value="old_value"
        )
        
        updated_config = AppConfiguration(
            id=1,
            config_key=config_key,
            config_value=config_value
        )
        
        self.mock_repository.get_by_key.return_value = existing_config
        self.mock_repository.update.return_value = updated_config
        
        # Act
        result = self.service.set_configuration_value(config_key, config_value)
        
        # Assert
        self.mock_repository.update.assert_called_once()
        assert result.config_value == config_value