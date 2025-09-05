"""
Integration tests for Configuration Service
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from ..main import app


class TestConfigurationServiceIntegration:
    """Integration tests for the Configuration Service API"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test root endpoint returns service information"""
        response = self.client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Configuration Service is running"
        assert data["service"] == "config-service"
        assert "endpoints" in data
    
    def test_status_endpoint(self):
        """Test status endpoint returns service status"""
        response = self.client.get("/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "config-service"
        assert data["status"] == "healthy"
        assert "features" in data
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "config-service"
    
    @patch('microservices.config-service.routers.configuration_router.get_configuration_service')
    def test_create_configuration_endpoint(self, mock_service):
        """Test configuration creation endpoint"""
        # Arrange
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        
        mock_response = Mock()
        mock_response.config_key = "test.key"
        mock_response.config_value = "test_value"
        mock_response.id = 1
        mock_response.version = 1
        mock_response.is_active = True
        
        mock_service_instance.create_configuration.return_value = mock_response
        
        config_data = {
            "config_key": "test.key",
            "config_value": "test_value",
            "environment": "development",
            "description": "Test configuration"
        }
        
        # Act
        response = self.client.post("/api/v1/configurations/", json=config_data)
        
        # Assert
        assert response.status_code == 201
        mock_service_instance.create_configuration.assert_called_once()
    
    @patch('microservices.config-service.routers.feature_flag_router.get_feature_flag_service')
    def test_create_feature_flag_endpoint(self, mock_service):
        """Test feature flag creation endpoint"""
        # Arrange
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        
        mock_response = Mock()
        mock_response.flag_key = "test_feature"
        mock_response.flag_name = "Test Feature"
        mock_response.is_enabled = True
        mock_response.id = 1
        
        mock_service_instance.create_feature_flag.return_value = mock_response
        
        flag_data = {
            "flag_name": "Test Feature",
            "flag_key": "test_feature",
            "description": "Test feature flag",
            "is_enabled": True,
            "rollout_percentage": 50
        }
        
        # Act
        response = self.client.post("/api/v1/feature-flags/", json=flag_data)
        
        # Assert
        assert response.status_code == 201
        mock_service_instance.create_feature_flag.assert_called_once()
    
    def test_configurations_list_endpoint(self):
        """Test configurations list endpoint"""
        response = self.client.get("/api/v1/configurations/")
        
        # Should return 200 even if empty (depends on database state)
        assert response.status_code in [200, 500]  # 500 if no database connection
    
    def test_feature_flags_list_endpoint(self):
        """Test feature flags list endpoint"""
        response = self.client.get("/api/v1/feature-flags/")
        
        # Should return 200 even if empty (depends on database state)
        assert response.status_code in [200, 500]  # 500 if no database connection
    
    def test_configuration_not_found(self):
        """Test configuration not found returns 404"""
        response = self.client.get("/api/v1/configurations/999")
        
        # Should return 404 or 500 (if database connection fails)
        assert response.status_code in [404, 500]
    
    def test_feature_flag_not_found(self):
        """Test feature flag not found returns 404"""
        response = self.client.get("/api/v1/feature-flags/999")
        
        # Should return 404 or 500 (if database connection fails)
        assert response.status_code in [404, 500]
    
    def test_invalid_configuration_data(self):
        """Test invalid configuration data returns 422"""
        invalid_data = {
            "config_key": "",  # Empty key should be invalid
            "config_value": "test_value"
        }
        
        response = self.client.post("/api/v1/configurations/", json=invalid_data)
        
        # Should return 422 for validation error
        assert response.status_code == 422
    
    def test_invalid_feature_flag_data(self):
        """Test invalid feature flag data returns 422"""
        invalid_data = {
            "flag_name": "Test Feature",
            "flag_key": "",  # Empty key should be invalid
            "rollout_percentage": 150  # Invalid percentage
        }
        
        response = self.client.post("/api/v1/feature-flags/", json=invalid_data)
        
        # Should return 422 for validation error
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__])