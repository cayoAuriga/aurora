"""
Comprehensive integration tests for service discovery and configuration
"""
import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock

from ..service_discovery import (
    ServiceRegistry,
    ServiceDiscoveryClient,
    ConfigurationClient,
    ServiceInfo,
    get_service_registry,
    get_discovery_client,
    get_config_client
)
from ..health_checks import create_standard_health_checks, HealthStatus
from ..config_loader import ConfigurationManager, ServiceConfig
from ..config_schemas import (
    ServiceRegistrationRequest,
    HealthCheckRequest,
    ConfigurationValueRequest,
    FeatureFlagCheckRequest,
    ConfigurationValidator,
    StandardConfigKeys,
    StandardFeatureFlags
)


class TestServiceDiscoveryIntegration:
    """Integration tests for service discovery functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.registry = ServiceRegistry()
        self.discovery_client = ServiceDiscoveryClient(self.registry)
        self.config_client = ConfigurationClient(self.discovery_client)
    
    @pytest.mark.asyncio
    async def test_complete_service_lifecycle(self):
        """Test complete service registration, discovery, and deregistration"""
        # Test service registration
        registration_data = ServiceRegistrationRequest(
            service_name="test-service",
            host="localhost",
            port=8001,
            health_endpoint="/health/ready",
            metadata={"version": "1.0.0", "environment": "test"}
        )
        
        success = await self.discovery_client.register_self(
            service_name=registration_data.service_name,
            host=registration_data.host,
            port=registration_data.port,
            health_endpoint=registration_data.health_endpoint,
            metadata=registration_data.metadata
        )
        
        assert success is True
        
        # Test service discovery
        discovered_url = await self.discovery_client.discover_service("test-service")
        assert discovered_url == "http://localhost:8001"
        
        # Test service info retrieval
        service_info = await self.registry.get_service("test-service")
        assert service_info is not None
        assert service_info.service_name == "test-service"
        assert service_info.metadata["version"] == "1.0.0"
        
        # Test heartbeat
        heartbeat_success = await self.discovery_client.send_heartbeat("test-service")
        assert heartbeat_success is True
        
        # Test health check (mock HTTP response)
        with patch.object(self.discovery_client, '_http_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_client.get = AsyncMock(return_value=mock_response)
            
            health_result = await self.discovery_client.health_check_service("test-service")
            assert health_result is True
        
        # Test service deregistration
        deregister_success = await self.registry.deregister_service("test-service")
        assert deregister_success is True
        
        # Verify service is gone
        service_info = await self.registry.get_service("test-service")
        assert service_info is None
    
    @pytest.mark.asyncio
    async def test_multiple_services_management(self):
        """Test managing multiple services simultaneously"""
        services = [
            ("api-gateway", "localhost", 8000),
            ("config-service", "localhost", 8004),
            ("subject-service", "localhost", 8002)
        ]
        
        # Register all services
        for service_name, host, port in services:
            success = await self.discovery_client.register_self(
                service_name=service_name,
                host=host,
                port=port,
                metadata={"test": True}
            )
            assert success is True
        
        # Test bulk operations
        all_services = await self.registry.get_all_services()
        assert len(all_services) == 3
        
        healthy_services = await self.registry.get_healthy_services()
        assert len(healthy_services) == 3
        
        # Test bulk health checks
        with patch.object(self.discovery_client, '_http_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_client.get = AsyncMock(return_value=mock_response)
            
            health_results = await self.discovery_client.health_check_all_services()
            assert len(health_results) == 3
            assert all(health_results.values())
        
        # Test stale service cleanup
        # Make one service stale
        service = await self.registry.get_service("config-service")
        service.last_heartbeat = time.time() - 120
        
        cleaned_count = await self.registry.cleanup_stale_services(timeout_seconds=60)
        assert cleaned_count == 1
        
        remaining_services = await self.registry.get_all_services()
        assert len(remaining_services) == 2
    
    @pytest.mark.asyncio
    async def test_service_discovery_with_health_checks(self):
        """Test service discovery integration with health checks"""
        # Register a service
        await self.discovery_client.register_self(
            service_name="health-test-service",
            host="localhost",
            port=8005
        )
        
        # Create health check manager
        health_manager = create_standard_health_checks("health-test-service", self.discovery_client)
        
        # Test health check execution
        health_status = await health_manager.get_overall_health()
        
        assert "service" in health_status
        assert health_status["service"] == "health-test-service"
        assert "status" in health_status
        assert "checks" in health_status
        assert "summary" in health_status
        
        # Verify standard checks are present
        checks = health_status["checks"]
        assert "database" in checks
        assert "memory" in checks
        assert "disk" in checks


class TestConfigurationIntegration:
    """Integration tests for configuration management"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.registry = ServiceRegistry()
        self.discovery_client = ServiceDiscoveryClient(self.registry)
        self.config_client = ConfigurationClient(self.discovery_client)
        self.config_manager = ConfigurationManager()
    
    @pytest.mark.asyncio
    async def test_configuration_loading_workflow(self):
        """Test complete configuration loading workflow"""
        # Register config service
        await self.discovery_client.register_self(
            service_name="config-service",
            host="localhost",
            port=8004
        )
        
        # Mock configuration responses
        with patch.object(self.config_client, '_http_client') as mock_client:
            # Mock bulk configuration response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "configurations": {
                    StandardConfigKeys.LOG_LEVEL: "INFO",
                    StandardConfigKeys.DB_CONNECTION_POOL_SIZE: 10,
                    StandardConfigKeys.HTTP_TIMEOUT: 30.0
                }
            }
            mock_client.get = AsyncMock(return_value=mock_response)
            
            # Test configuration retrieval
            configs = await self.config_client.get_bulk_configurations(
                environment="development",
                service_name="test-service"
            )
            
            assert StandardConfigKeys.LOG_LEVEL in configs
            assert configs[StandardConfigKeys.LOG_LEVEL] == "INFO"
            assert configs[StandardConfigKeys.DB_CONNECTION_POOL_SIZE] == 10
    
    @pytest.mark.asyncio
    async def test_feature_flag_evaluation(self):
        """Test feature flag evaluation workflow"""
        # Register config service
        await self.discovery_client.register_self(
            service_name="config-service",
            host="localhost",
            port=8004
        )
        
        # Mock feature flag responses
        with patch.object(self.config_client, '_http_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "flag_key": StandardFeatureFlags.ENABLE_DETAILED_LOGGING,
                "enabled": True
            }
            mock_client.get = AsyncMock(return_value=mock_response)
            
            # Test feature flag check
            enabled = await self.config_client.is_feature_enabled(
                StandardFeatureFlags.ENABLE_DETAILED_LOGGING,
                user_id=123
            )
            
            assert enabled is True
    
    @pytest.mark.asyncio
    async def test_service_config_validation(self):
        """Test service configuration validation"""
        # Create service config
        service_config = await self.config_manager.get_service_config(
            "test-service",
            load_remote=False
        )
        
        # Test validation
        validation_result = await self.config_manager.validate_service_config("test-service")
        
        assert "valid" in validation_result
        assert "errors" in validation_result
        assert "warnings" in validation_result
        assert validation_result["service_name"] == "test-service"
    
    @pytest.mark.asyncio
    async def test_configuration_caching(self):
        """Test configuration caching behavior"""
        # Register config service
        await self.discovery_client.register_self(
            service_name="config-service",
            host="localhost",
            port=8004
        )
        
        with patch.object(self.config_client, '_http_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"key": "test.key", "value": "cached_value"}
            mock_client.get = AsyncMock(return_value=mock_response)
            
            # First request
            value1 = await self.config_client.get_configuration("test.key", use_cache=True)
            
            # Second request (should use cache)
            value2 = await self.config_client.get_configuration("test.key", use_cache=True)
            
            assert value1 == "cached_value"
            assert value2 == "cached_value"
            
            # HTTP client should only be called once due to caching
            assert mock_client.get.call_count == 1
            
            # Clear cache and test again
            self.config_client.clear_cache()
            
            value3 = await self.config_client.get_configuration("test.key", use_cache=True)
            assert value3 == "cached_value"
            assert mock_client.get.call_count == 2


class TestConfigurationSchemas:
    """Test configuration schemas and validation"""
    
    def test_service_registration_request_validation(self):
        """Test service registration request validation"""
        # Valid request
        valid_request = ServiceRegistrationRequest(
            service_name="test-service",
            host="localhost",
            port=8000
        )
        assert valid_request.service_name == "test-service"
        
        # Invalid service name
        with pytest.raises(ValueError):
            ServiceRegistrationRequest(
                service_name="Test-Service",  # Uppercase not allowed
                host="localhost",
                port=8000
            )
        
        # Invalid port
        with pytest.raises(ValueError):
            ServiceRegistrationRequest(
                service_name="test-service",
                host="localhost",
                port=70000  # Port too high
            )
    
    def test_configuration_value_request_validation(self):
        """Test configuration value request validation"""
        # Valid request
        valid_request = ConfigurationValueRequest(
            config_key="database.connection_pool.size",
            environment="development"
        )
        assert valid_request.config_key == "database.connection_pool.size"
        
        # Invalid config key
        with pytest.raises(ValueError):
            ConfigurationValueRequest(
                config_key="123invalid",  # Cannot start with number
                environment="development"
            )
    
    def test_feature_flag_check_request_validation(self):
        """Test feature flag check request validation"""
        # Valid request
        valid_request = FeatureFlagCheckRequest(
            flag_key="enable_new_feature",
            user_id=123
        )
        assert valid_request.flag_key == "enable_new_feature"
        
        # Invalid flag key
        with pytest.raises(ValueError):
            FeatureFlagCheckRequest(
                flag_key="Enable-New-Feature",  # Hyphens not allowed
                user_id=123
            )
    
    def test_configuration_validator(self):
        """Test configuration validator utility"""
        validator = ConfigurationValidator()
        
        # Test service name validation
        assert validator.validate_service_name("test-service") is True
        assert validator.validate_service_name("Test-Service") is False
        assert validator.validate_service_name("test_service") is False
        
        # Test config key validation
        assert validator.validate_config_key("database.pool.size") is True
        assert validator.validate_config_key("123invalid") is False
        
        # Test flag key validation
        assert validator.validate_flag_key("enable_feature") is True
        assert validator.validate_flag_key("Enable_Feature") is False
        
        # Test port validation
        assert validator.validate_port(8000) is True
        assert validator.validate_port(0) is False
        assert validator.validate_port(70000) is False
        
        # Test environment validation
        assert validator.validate_environment("development") is True
        assert validator.validate_environment("invalid") is False


class TestEndToEndIntegration:
    """End-to-end integration tests"""
    
    @pytest.mark.asyncio
    async def test_complete_microservices_workflow(self):
        """Test complete workflow from service registration to configuration loading"""
        registry = ServiceRegistry()
        discovery_client = ServiceDiscoveryClient(registry)
        config_client = ConfigurationClient(discovery_client)
        config_manager = ConfigurationManager()
        
        # Step 1: Register services
        services = ["api-gateway", "config-service", "subject-service"]
        for i, service_name in enumerate(services):
            success = await discovery_client.register_self(
                service_name=service_name,
                host="localhost",
                port=8000 + i,
                metadata={"version": "1.0.0", "environment": "test"}
            )
            assert success is True
        
        # Step 2: Verify service discovery
        all_services = await registry.get_all_services()
        assert len(all_services) == 3
        
        service_names = [s.service_name for s in all_services]
        for service_name in services:
            assert service_name in service_names
        
        # Step 3: Test health checks
        health_manager = create_standard_health_checks("api-gateway", discovery_client)
        health_status = await health_manager.get_overall_health()
        
        assert health_status["service"] == "api-gateway"
        assert "status" in health_status
        
        # Step 4: Test configuration loading (with mocked responses)
        with patch.object(config_client, '_http_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "configurations": {
                    StandardConfigKeys.LOG_LEVEL: "DEBUG",
                    StandardConfigKeys.HTTP_TIMEOUT: 60
                }
            }
            mock_client.get = AsyncMock(return_value=mock_response)
            
            # Load configuration for a service
            service_config = await config_manager.get_service_config("api-gateway", load_remote=False)
            
            # Manually load remote configs to test
            await service_config.load_remote_configurations(config_client)
            
            assert len(service_config.remote_configs) > 0
        
        # Step 5: Test feature flags
        with patch.object(config_client, '_http_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "flag_key": StandardFeatureFlags.ENABLE_DETAILED_LOGGING,
                "enabled": True
            }
            mock_client.get = AsyncMock(return_value=mock_response)
            
            enabled = await config_manager.get_feature_flag_status(
                "api-gateway",
                StandardFeatureFlags.ENABLE_DETAILED_LOGGING
            )
            assert enabled is True
        
        # Step 6: Cleanup
        for service_name in services:
            await registry.deregister_service(service_name)
        
        final_services = await registry.get_all_services()
        assert len(final_services) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])