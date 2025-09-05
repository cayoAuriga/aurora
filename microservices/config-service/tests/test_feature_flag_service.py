"""
Unit tests for Feature Flag Service
"""
import pytest
from unittest.mock import Mock
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..services.feature_flag_service import FeatureFlagService
from ..schemas.feature_flag import FeatureFlagCreate, FeatureFlagUpdate, EnvironmentType
from ..models.feature_flag import FeatureFlag
from shared.errors import NotFoundError, ValidationError


class TestFeatureFlagService:
    """Test cases for FeatureFlagService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = Mock(spec=Session)
        self.service = FeatureFlagService(self.mock_db)
        self.mock_repository = Mock()
        self.service.repository = self.mock_repository
    
    def test_create_feature_flag_success(self):
        """Test successful feature flag creation"""
        # Arrange
        flag_data = FeatureFlagCreate(
            flag_name="Test Feature",
            flag_key="test_feature",
            description="Test feature flag",
            is_enabled=True,
            rollout_percentage=50
        )
        
        mock_flag = FeatureFlag(
            id=1,
            flag_name="Test Feature",
            flag_key="test_feature",
            description="Test feature flag",
            is_enabled=True,
            rollout_percentage=50
        )
        
        self.mock_repository.create.return_value = mock_flag
        
        # Act
        result = self.service.create_feature_flag(flag_data)
        
        # Assert
        self.mock_repository.create.assert_called_once_with(flag_data)
        assert result.flag_key == "test_feature"
        assert result.is_enabled is True
        assert result.rollout_percentage == 50
    
    def test_create_feature_flag_duplicate_key(self):
        """Test feature flag creation with duplicate key"""
        # Arrange
        flag_data = FeatureFlagCreate(
            flag_name="Duplicate Feature",
            flag_key="duplicate_feature"
        )
        
        self.mock_repository.create.side_effect = ValueError("Feature flag already exists")
        
        # Act & Assert
        with pytest.raises(ValidationError):
            self.service.create_feature_flag(flag_data)
    
    def test_get_feature_flag_success(self):
        """Test successful feature flag retrieval"""
        # Arrange
        flag_id = 1
        mock_flag = FeatureFlag(
            id=flag_id,
            flag_name="Test Feature",
            flag_key="test_feature"
        )
        
        self.mock_repository.get_by_id.return_value = mock_flag
        
        # Act
        result = self.service.get_feature_flag(flag_id)
        
        # Assert
        self.mock_repository.get_by_id.assert_called_once_with(flag_id)
        assert result.id == flag_id
        assert result.flag_key == "test_feature"
    
    def test_get_feature_flag_not_found(self):
        """Test feature flag retrieval when not found"""
        # Arrange
        flag_id = 999
        self.mock_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(NotFoundError):
            self.service.get_feature_flag(flag_id)
    
    def test_evaluate_feature_flag_enabled(self):
        """Test feature flag evaluation when enabled"""
        # Arrange
        flag_key = "test_feature"
        user_id = 123
        
        evaluation_result = {
            "flag_key": flag_key,
            "is_enabled": True,
            "user_qualified": True,
            "reason": "User qualifies for rollout",
            "rollout_percentage": 100,
            "expires_at": None
        }
        
        self.mock_repository.evaluate_flag.return_value = evaluation_result
        
        # Act
        result = self.service.evaluate_feature_flag(flag_key, user_id)
        
        # Assert
        self.mock_repository.evaluate_flag.assert_called_once_with(flag_key, user_id, None)
        assert result.flag_key == flag_key
        assert result.is_enabled is True
        assert result.user_qualified is True
    
    def test_evaluate_feature_flag_disabled(self):
        """Test feature flag evaluation when disabled"""
        # Arrange
        flag_key = "disabled_feature"
        
        evaluation_result = {
            "flag_key": flag_key,
            "is_enabled": False,
            "user_qualified": False,
            "reason": "Flag is disabled",
            "rollout_percentage": 0,
            "expires_at": None
        }
        
        self.mock_repository.evaluate_flag.return_value = evaluation_result
        
        # Act
        result = self.service.evaluate_feature_flag(flag_key)
        
        # Assert
        assert result.flag_key == flag_key
        assert result.is_enabled is False
        assert result.user_qualified is False
        assert result.reason == "Flag is disabled"
    
    def test_toggle_feature_flag_success(self):
        """Test successful feature flag toggle"""
        # Arrange
        flag_key = "test_feature"
        enabled = True
        
        mock_flag = FeatureFlag(
            id=1,
            flag_key=flag_key,
            is_enabled=False
        )
        
        updated_flag = FeatureFlag(
            id=1,
            flag_key=flag_key,
            is_enabled=enabled
        )
        
        self.mock_repository.get_by_key.return_value = mock_flag
        self.mock_repository.update.return_value = updated_flag
        
        # Act
        result = self.service.toggle_feature_flag(flag_key, enabled)
        
        # Assert
        self.mock_repository.get_by_key.assert_called_once_with(flag_key)
        self.mock_repository.update.assert_called_once()
        assert result.is_enabled == enabled
    
    def test_toggle_feature_flag_not_found(self):
        """Test feature flag toggle when flag not found"""
        # Arrange
        flag_key = "nonexistent_feature"
        self.mock_repository.get_by_key.return_value = None
        
        # Act & Assert
        with pytest.raises(NotFoundError):
            self.service.toggle_feature_flag(flag_key, True)
    
    def test_update_rollout_percentage_success(self):
        """Test successful rollout percentage update"""
        # Arrange
        flag_key = "test_feature"
        percentage = 75
        
        mock_flag = FeatureFlag(
            id=1,
            flag_key=flag_key,
            rollout_percentage=50
        )
        
        updated_flag = FeatureFlag(
            id=1,
            flag_key=flag_key,
            rollout_percentage=percentage
        )
        
        self.mock_repository.get_by_key.return_value = mock_flag
        self.mock_repository.update.return_value = updated_flag
        
        # Act
        result = self.service.update_rollout_percentage(flag_key, percentage)
        
        # Assert
        assert result.rollout_percentage == percentage
    
    def test_update_rollout_percentage_invalid(self):
        """Test rollout percentage update with invalid value"""
        # Arrange
        flag_key = "test_feature"
        invalid_percentage = 150
        
        # Act & Assert
        with pytest.raises(ValidationError):
            self.service.update_rollout_percentage(flag_key, invalid_percentage)
    
    def test_is_feature_enabled_true(self):
        """Test is_feature_enabled returns True"""
        # Arrange
        flag_key = "enabled_feature"
        
        evaluation_result = {
            "flag_key": flag_key,
            "is_enabled": True,
            "user_qualified": True,
            "reason": "User qualifies for rollout",
            "rollout_percentage": 100,
            "expires_at": None
        }
        
        self.mock_repository.evaluate_flag.return_value = evaluation_result
        
        # Act
        result = self.service.is_feature_enabled(flag_key)
        
        # Assert
        assert result is True
    
    def test_is_feature_enabled_false(self):
        """Test is_feature_enabled returns False"""
        # Arrange
        flag_key = "disabled_feature"
        
        evaluation_result = {
            "flag_key": flag_key,
            "is_enabled": False,
            "user_qualified": False,
            "reason": "Flag is disabled",
            "rollout_percentage": 0,
            "expires_at": None
        }
        
        self.mock_repository.evaluate_flag.return_value = evaluation_result
        
        # Act
        result = self.service.is_feature_enabled(flag_key)
        
        # Assert
        assert result is False
    
    def test_delete_feature_flag_success(self):
        """Test successful feature flag deletion"""
        # Arrange
        flag_id = 1
        self.mock_repository.delete.return_value = True
        
        # Act
        result = self.service.delete_feature_flag(flag_id)
        
        # Assert
        self.mock_repository.delete.assert_called_once_with(flag_id)
        assert result is True
    
    def test_delete_feature_flag_not_found(self):
        """Test feature flag deletion when not found"""
        # Arrange
        flag_id = 999
        self.mock_repository.delete.return_value = False
        
        # Act & Assert
        with pytest.raises(NotFoundError):
            self.service.delete_feature_flag(flag_id)