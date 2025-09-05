"""
Tests for service discovery functionality
"""
import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock

from ..service_discovery import (
    ServiceInfo,
    ServiceRegistry,
    ServiceDiscoveryClient,
    ConfigurationClient
)


class TestServiceInfo:
    """Test ServiceInfo dataclass"""
    
    def test_service_info_creation(self):
        """Test ServiceInfo creation with defaults"""
        service = ServiceInfo(
            service_name="test-service",
            host="localhost",
            port=8000
        )
        
        assert service.service_name == "test-service"
        assert service.host == "localhost"
        assert service.port == 8000
        assert service.health_endpoint == "/health"
        assert service.status == "healthy"
        assert service.metadata == {}
        assert service.last_heartbeat > 0
    
    def test_service_info_urls(self):
        """Test URL generation"""
        service = ServiceInfo(
            service_name="test-service",
            host="localhost",
            port=8000,
            health_endpoint="/health/ready"
        )
        
        assert service.base_url == "http://localhost:8000"
        assert service.health_url == "http://localhost:8000/health/ready"
    
    def test_service_info_health_check(self):
        """Test health status checking"""
        service = ServiceInfo(
            service_name="test-service",
            host="localhost",
            port=8000
        )
        
        # Should be healthy immediately
        assert service.is_healthy(timeout_seconds=30)
        
        # Simulate old heartbeat
        service.last_heartbeat = time.time() - 60
        assert not service.is_healthy(timeout_seconds=30)


class TestServiceRegistry:
    """Test ServiceRegistry class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.registry = ServiceRegistry()
    
    @pytest.mark.asyncio
    async def test_register_service(self):
        """Test service registration"""
        service = ServiceInfo(
            service_name="test-service",
            host="localhost",
            port=8000
        )
        
        result = await self.registry.register_service(service)
        assert result is True
        
        # Verify service is registered
        registered_service = await self.registry.get_service("test-service")
        assert registered_service is not None
        assert registered_service.service_name == "test-service"
    
    @pytest.mark.asyncio
    async def test_deregister_service(self):
        """Test service deregistration"""
        service = ServiceInfo(
            service_name="test-service",
            host="localhost",
            port=8000
        )
        
        # Register first
        await self.registry.register_service(service)
        
        # Then deregister
        result = await self.registry.deregister_service("test-service")
        assert result is True
        
        # Verify service is gone
        registered_service = await self.registry.get_service("test-service")
        assert registered_service is None
    
    @pytest.mark.asyncio
    async def test_get_all_services(self):
        """Test getting all services"""
        services = [
            ServiceInfo("service-1", "localhost", 8001),
            ServiceInfo("service-2", "localhost", 8002),
            ServiceInfo("service-3", "localhost", 8003)
        ]
        
        for service in services:
            await self.registry.register_service(service)
        
        all_services = await self.registry.get_all_services()
        assert len(all_services) == 3
        
        service_names = [s.service_name for s in all_services]
        assert "service-1" in service_names
        assert "service-2" in service_names
        assert "service-3" in service_names
    
    @pytest.mark.asyncio
    async def test_get_healthy_services(self):
        """Test getting only healthy services"""
        # Register services
        service1 = ServiceInfo("service-1", "localhost", 8001)
        service2 = ServiceInfo("service-2", "localhost", 8002)
        
        await self.registry.register_service(service1)
        await self.registry.register_service(service2)
        
        # Make one service stale
        service1.last_heartbeat = time.time() - 60
        
        healthy_services = await self.registry.get_healthy_services(timeout_seconds=30)
        assert len(healthy_services) == 1
        assert healthy_services[0].service_name == "service-2"
    
    @pytest.mark.asyncio
    async def test_update_heartbeat(self):
        """Test heartbeat update"""
        service = ServiceInfo("test-service", "localhost", 8000)
        await self.registry.register_service(service)
        
        # Get initial heartbeat
        initial_heartbeat = service.last_heartbeat
        
        # Wait a bit and update heartbeat
        await asyncio.sleep(0.1)
        result = await self.registry.update_heartbeat("test-service")
        assert result is True
        
        # Verify heartbeat was updated
        updated_service = await self.registry.get_service("test-service")
        assert updated_service.last_heartbeat > initial_heartbeat
    
    @pytest.mark.asyncio
    async def test_cleanup_stale_services(self):
        """Test cleanup of stale services"""
        # Register services
        service1 = ServiceInfo("service-1", "localhost", 8001)
        service2 = ServiceInfo("service-2", "localhost", 8002)
        
        await self.registry.register_service(service1)
        await self.registry.register_service(service2)
        
        # Make one service stale
        service1.last_heartbeat = time.time() - 120
        
        # Cleanup stale services
        cleaned_count = await self.registry.cleanup_stale_services(timeout_seconds=60)
        assert cleaned_count == 1
        
        # Verify only healthy service remains
        all_services = await self.registry.get_all_services()
        assert len(all_services) == 1
        assert all_services[0].service_name == "service-2"


class TestServiceDiscoveryClient:
    """Test ServiceDiscoveryClient class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.registry = ServiceRegistry()
        self.client = ServiceDiscoveryClient(self.registry)
    
    @pytest.mark.asyncio
    async def test_register_self(self):
        """Test self-registration"""
        result = await self.client.register_self(
            service_name="test-service",
            host="localhost",
            port=8000,
            metadata={"version": "1.0.0"}
        )
        
        assert result is True
        
        # Verify registration
        service = await self.registry.get_service("test-service")
        assert service is not None
        assert service.metadata["version"] == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_discover_service(self):
        """Test service discovery"""
        # Register a service
        await self.client.register_self("test-service", "localhost", 8000)
        
        # Discover it
        base_url = await self.client.discover_service("test-service")
        assert base_url == "http://localhost:8000"
        
        # Try to discover non-existent service
        base_url = await self.client.discover_service("non-existent")
        assert base_url is None
    
    @pytest.mark.asyncio
    async def test_get_service_url(self):
        """Test getting service URL with path"""
        # Register a service
        await self.client.register_self("test-service", "localhost", 8000)
        
        # Get URL with path
        url = await self.client.get_service_url("test-service", "/api/v1/test")
        assert url == "http://localhost:8000/api/v1/test"
        
        # Try with non-existent service
        url = await self.client.get_service_url("non-existent", "/api/v1/test")
        assert url is None
    
    @pytest.mark.asyncio
    async def test_health_check_service(self):
        """Test health checking a service"""
        # Register a service
        await self.client.register_self("test-service", "localhost", 8000)
        
        # Mock HTTP client
        with patch.object(self.client, '_http_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_client.get = AsyncMock(return_value=mock_response)
            
            # Health check should pass
            result = await self.client.health_check_service("test-service")
            assert result is True
            
            # Verify HTTP call was made
            mock_client.get.assert_called_once_with("http://localhost:8000/health")
    
    @pytest.mark.asyncio
    async def test_health_check_service_failure(self):
        """Test health check failure"""
        # Register a service
        await self.client.register_self("test-service", "localhost", 8000)
        
        # Mock HTTP client to fail
        with patch.object(self.client, '_http_client') as mock_client:
            mock_client.get = AsyncMock(side_effect=Exception("Connection failed"))
            
            # Health check should fail
            result = await self.client.health_check_service("test-service")
            assert result is False
    
    @pytest.mark.asyncio
    async def test_health_check_all_services(self):
        """Test health checking all services"""
        # Register multiple services
        await self.client.register_self("service-1", "localhost", 8001)
        await self.client.register_self("service-2", "localhost", 8002)
        
        # Mock HTTP client
        with patch.object(self.client, '_http_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_client.get = AsyncMock(return_value=mock_response)
            
            # Health check all services
            results = await self.client.health_check_all_services()
            
            assert len(results) == 2
            assert results["service-1"] is True
            assert results["service-2"] is True
    
    @pytest.mark.asyncio
    async def test_send_heartbeat(self):
        """Test sending heartbeat"""
        # Register a service
        await self.client.register_self("test-service", "localhost", 8000)
        
        # Send heartbeat
        result = await self.client.send_heartbeat("test-service")
        assert result is True
        
        # Try with non-existent service
        result = await self.client.send_heartbeat("non-existent")
        assert result is False


class TestConfigurationClient:
    """Test ConfigurationClient class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.registry = ServiceRegistry()
        self.discovery_client = ServiceDiscoveryClient(self.registry)
        self.config_client = ConfigurationClient(self.discovery_client)
    
    @pytest.mark.asyncio
    async def test_get_configuration_success(self):
        """Test successful configuration retrieval"""
        # Register config service
        await self.discovery_client.register_self("config-service", "localhost", 8004)
        
        # Mock HTTP response
        with patch.object(self.config_client, '_http_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"key": "test.key", "value": "test_value"}
            mock_client.get = AsyncMock(return_value=mock_response)
            
            # Get configuration
            value = await self.config_client.get_configuration("test.key")
            assert value == "test_value"
    
    @pytest.mark.asyncio
    async def test_get_configuration_service_unavailable(self):
        """Test configuration retrieval when service is unavailable"""
        # Don't register config service
        
        # Get configuration should return default
        value = await self.config_client.get_configuration("test.key", default_value="default")
        assert value == "default"
    
    @pytest.mark.asyncio
    async def test_get_configuration_caching(self):
        """Test configuration caching"""
        # Register config service
        await self.discovery_client.register_self("config-service", "localhost", 8004)
        
        # Mock HTTP response
        with patch.object(self.config_client, '_http_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"key": "test.key", "value": "test_value"}
            mock_client.get = AsyncMock(return_value=mock_response)
            
            # Get configuration twice
            value1 = await self.config_client.get_configuration("test.key", use_cache=True)
            value2 = await self.config_client.get_configuration("test.key", use_cache=True)
            
            assert value1 == "test_value"
            assert value2 == "test_value"
            
            # HTTP client should only be called once due to caching
            assert mock_client.get.call_count == 1
    
    @pytest.mark.asyncio
    async def test_is_feature_enabled(self):
        """Test feature flag checking"""
        # Register config service
        await self.discovery_client.register_self("config-service", "localhost", 8004)
        
        # Mock HTTP response
        with patch.object(self.config_client, '_http_client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"flag_key": "test_feature", "enabled": True}
            mock_client.get = AsyncMock(return_value=mock_response)
            
            # Check feature flag
            enabled = await self.config_client.is_feature_enabled("test_feature")
            assert enabled is True
    
    @pytest.mark.asyncio
    async def test_clear_cache(self):
        """Test cache clearing"""
        # Add something to cache
        self.config_client._config_cache["test"] = "value"
        self.config_client._cache_timestamps["test"] = time.time()
        
        # Clear cache
        self.config_client.clear_cache()
        
        assert len(self.config_client._config_cache) == 0
        assert len(self.config_client._cache_timestamps) == 0


if __name__ == "__main__":
    pytest.main([__file__])