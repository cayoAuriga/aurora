"""
Service Discovery functionality for Aurora microservices
"""
import asyncio
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import httpx
import logging

logger = logging.getLogger(__name__)


@dataclass
class ServiceInfo:
    """Service information for registry"""
    service_name: str
    host: str
    port: int
    health_endpoint: str = "/health"
    status: str = "healthy"
    last_heartbeat: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.last_heartbeat == 0.0:
            self.last_heartbeat = time.time()
    
    @property
    def base_url(self) -> str:
        """Get the base URL for this service"""
        return f"http://{self.host}:{self.port}"
    
    @property
    def health_url(self) -> str:
        """Get the health check URL for this service"""
        return f"{self.base_url}{self.health_endpoint}"
    
    def is_healthy(self, timeout_seconds: int = 30) -> bool:
        """Check if service is considered healthy based on last heartbeat"""
        return (time.time() - self.last_heartbeat) < timeout_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class ServiceRegistry:
    """In-memory service registry for development/testing"""
    
    def __init__(self):
        self._services: Dict[str, ServiceInfo] = {}
        self._lock = asyncio.Lock()
    
    async def register_service(self, service_info: ServiceInfo) -> bool:
        """Register a service in the registry"""
        async with self._lock:
            service_info.last_heartbeat = time.time()
            self._services[service_info.service_name] = service_info
            logger.info(f"Registered service: {service_info.service_name} at {service_info.base_url}")
            return True
    
    async def deregister_service(self, service_name: str) -> bool:
        """Remove a service from the registry"""
        async with self._lock:
            if service_name in self._services:
                del self._services[service_name]
                logger.info(f"Deregistered service: {service_name}")
                return True
            return False
    
    async def get_service(self, service_name: str) -> Optional[ServiceInfo]:
        """Get service information by name"""
        async with self._lock:
            return self._services.get(service_name)
    
    async def get_all_services(self) -> List[ServiceInfo]:
        """Get all registered services"""
        async with self._lock:
            return list(self._services.values())
    
    async def get_healthy_services(self, timeout_seconds: int = 30) -> List[ServiceInfo]:
        """Get all healthy services"""
        async with self._lock:
            return [
                service for service in self._services.values()
                if service.is_healthy(timeout_seconds)
            ]
    
    async def update_heartbeat(self, service_name: str) -> bool:
        """Update service heartbeat"""
        async with self._lock:
            if service_name in self._services:
                self._services[service_name].last_heartbeat = time.time()
                return True
            return False
    
    async def cleanup_stale_services(self, timeout_seconds: int = 60):
        """Remove services that haven't sent heartbeat recently"""
        async with self._lock:
            current_time = time.time()
            stale_services = [
                name for name, service in self._services.items()
                if (current_time - service.last_heartbeat) > timeout_seconds
            ]
            
            for service_name in stale_services:
                del self._services[service_name]
                logger.warning(f"Removed stale service: {service_name}")
            
            return len(stale_services)


class ServiceDiscoveryClient:
    """Client for service discovery operations"""
    
    def __init__(self, registry: ServiceRegistry = None):
        self.registry = registry or ServiceRegistry()
        self._http_client = httpx.AsyncClient(timeout=10.0)
    
    async def register_self(
        self,
        service_name: str,
        host: str = "localhost",
        port: int = 8000,
        health_endpoint: str = "/health",
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Register current service"""
        service_info = ServiceInfo(
            service_name=service_name,
            host=host,
            port=port,
            health_endpoint=health_endpoint,
            metadata=metadata or {}
        )
        
        return await self.registry.register_service(service_info)
    
    async def discover_service(self, service_name: str) -> Optional[str]:
        """Discover a service and return its base URL"""
        service = await self.registry.get_service(service_name)
        if service and service.is_healthy():
            return service.base_url
        return None
    
    async def get_service_url(self, service_name: str, path: str = "") -> Optional[str]:
        """Get full URL for a service endpoint"""
        base_url = await self.discover_service(service_name)
        if base_url:
            return f"{base_url}{path}"
        return None
    
    async def health_check_service(self, service_name: str) -> bool:
        """Perform health check on a specific service"""
        service = await self.registry.get_service(service_name)
        if not service:
            return False
        
        try:
            response = await self._http_client.get(service.health_url)
            is_healthy = response.status_code == 200
            
            # Update service status
            service.status = "healthy" if is_healthy else "unhealthy"
            if is_healthy:
                await self.registry.update_heartbeat(service_name)
            
            return is_healthy
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            service.status = "unhealthy"
            return False
    
    async def health_check_all_services(self) -> Dict[str, bool]:
        """Perform health check on all registered services"""
        services = await self.registry.get_all_services()
        results = {}
        
        for service in services:
            results[service.service_name] = await self.health_check_service(service.service_name)
        
        return results
    
    async def send_heartbeat(self, service_name: str) -> bool:
        """Send heartbeat for a service"""
        return await self.registry.update_heartbeat(service_name)
    
    async def close(self):
        """Close HTTP client"""
        await self._http_client.aclose()


class ConfigurationClient:
    """Client for accessing Configuration Service"""
    
    def __init__(self, discovery_client: ServiceDiscoveryClient):
        self.discovery = discovery_client
        self._http_client = httpx.AsyncClient(timeout=10.0)
        self._config_cache: Dict[str, Any] = {}
        self._cache_ttl = 300  # 5 minutes
        self._cache_timestamps: Dict[str, float] = {}
    
    async def get_configuration(
        self,
        config_key: str,
        environment: str = "all",
        service_name: Optional[str] = None,
        default_value: Any = None,
        use_cache: bool = True
    ) -> Any:
        """Get configuration value from Configuration Service"""
        
        # Check cache first
        cache_key = f"{config_key}:{environment}:{service_name}"
        if use_cache and self._is_cache_valid(cache_key):
            return self._config_cache.get(cache_key, default_value)
        
        try:
            # Discover Configuration Service
            config_service_url = await self.discovery.get_service_url(
                "config-service",
                f"/api/v1/configurations/value/{config_key}"
            )
            
            if not config_service_url:
                logger.warning("Configuration Service not available")
                return default_value
            
            # Make request
            params = {"environment": environment}
            if service_name:
                params["service_name"] = service_name
            if default_value is not None:
                params["default_value"] = str(default_value)
            
            response = await self._http_client.get(config_service_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                value = data.get("value", default_value)
                
                # Cache the result
                if use_cache:
                    self._config_cache[cache_key] = value
                    self._cache_timestamps[cache_key] = time.time()
                
                return value
            else:
                logger.warning(f"Configuration request failed: {response.status_code}")
                return default_value
                
        except Exception as e:
            logger.error(f"Failed to get configuration {config_key}: {e}")
            return default_value
    
    async def get_bulk_configurations(
        self,
        environment: str = "all",
        service_name: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Get all configurations for a service/environment"""
        
        cache_key = f"bulk:{environment}:{service_name}"
        if use_cache and self._is_cache_valid(cache_key):
            return self._config_cache.get(cache_key, {})
        
        try:
            config_service_url = await self.discovery.get_service_url(
                "config-service",
                "/api/v1/configurations/bulk"
            )
            
            if not config_service_url:
                logger.warning("Configuration Service not available")
                return {}
            
            params = {"environment": environment}
            if service_name:
                params["service_name"] = service_name
            
            response = await self._http_client.get(config_service_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                configurations = data.get("configurations", {})
                
                # Cache the result
                if use_cache:
                    self._config_cache[cache_key] = configurations
                    self._cache_timestamps[cache_key] = time.time()
                
                return configurations
            else:
                logger.warning(f"Bulk configuration request failed: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Failed to get bulk configurations: {e}")
            return {}
    
    async def is_feature_enabled(
        self,
        flag_key: str,
        user_id: Optional[int] = None,
        environment: str = "all",
        use_cache: bool = True
    ) -> bool:
        """Check if a feature flag is enabled"""
        
        cache_key = f"flag:{flag_key}:{user_id}:{environment}"
        if use_cache and self._is_cache_valid(cache_key, ttl=60):  # Shorter TTL for flags
            return self._config_cache.get(cache_key, False)
        
        try:
            config_service_url = await self.discovery.get_service_url(
                "config-service",
                f"/api/v1/feature-flags/check/{flag_key}"
            )
            
            if not config_service_url:
                logger.warning("Configuration Service not available")
                return False
            
            params = {"environment": environment}
            if user_id:
                params["user_id"] = user_id
            
            response = await self._http_client.get(config_service_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                enabled = data.get("enabled", False)
                
                # Cache the result
                if use_cache:
                    self._config_cache[cache_key] = enabled
                    self._cache_timestamps[cache_key] = time.time()
                
                return enabled
            else:
                return False
                
        except Exception as e:
            logger.error(f"Failed to check feature flag {flag_key}: {e}")
            return False
    
    def _is_cache_valid(self, cache_key: str, ttl: Optional[int] = None) -> bool:
        """Check if cached value is still valid"""
        if cache_key not in self._cache_timestamps:
            return False
        
        age = time.time() - self._cache_timestamps[cache_key]
        return age < (ttl or self._cache_ttl)
    
    def clear_cache(self):
        """Clear configuration cache"""
        self._config_cache.clear()
        self._cache_timestamps.clear()
    
    async def close(self):
        """Close HTTP client"""
        await self._http_client.aclose()


# Global instances
_service_registry = ServiceRegistry()
_discovery_client = ServiceDiscoveryClient(_service_registry)
_config_client = ConfigurationClient(_discovery_client)


def get_service_registry() -> ServiceRegistry:
    """Get global service registry instance"""
    return _service_registry


def get_discovery_client() -> ServiceDiscoveryClient:
    """Get global service discovery client"""
    return _discovery_client


def get_config_client() -> ConfigurationClient:
    """Get global configuration client"""
    return _config_client


async def cleanup_discovery():
    """Cleanup discovery clients"""
    await _discovery_client.close()
    await _config_client.close()