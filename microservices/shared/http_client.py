"""
Shared HTTP client for inter-service communication
"""
import httpx
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging

from .config import BaseServiceConfig
from .errors import ExternalServiceError, CircuitBreakerError
from .utils import CircuitBreaker
from .aurora_logging import get_logger

logger = get_logger(__name__)


class ServiceClient:
    """HTTP client for inter-service communication"""
    
    def __init__(
        self,
        service_name: str,
        base_url: str,
        timeout: float = 30.0,
        retries: int = 3,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: int = 60
    ):
        self.service_name = service_name
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retries = retries
        
        # Circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_breaker_threshold,
            timeout=circuit_breaker_timeout
        )
        
        # HTTP client
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def _make_request(
        self,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> httpx.Response:
        """Make HTTP request with circuit breaker and retry logic"""
        
        # Prepare headers
        request_headers = {
            "Content-Type": "application/json",
            "User-Agent": f"Aurora-Service-Client/{self.service_name}"
        }
        
        if correlation_id:
            request_headers["X-Correlation-ID"] = correlation_id
        
        if headers:
            request_headers.update(headers)
        
        # Full URL
        url = f"{self.base_url}{path}"
        
        # Make request with circuit breaker
        try:
            response = self.circuit_breaker.call(
                self._execute_request,
                method=method,
                url=url,
                headers=request_headers,
                params=params,
                json=json,
                data=data
            )
            return await response
        except Exception as e:
            if self.circuit_breaker.state == 'OPEN':
                raise CircuitBreakerError(self.service_name, correlation_id)
            raise ExternalServiceError(self.service_name, str(e), correlation_id)
    
    async def _execute_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        """Execute HTTP request with retries"""
        
        last_exception = None
        
        for attempt in range(self.retries + 1):
            try:
                logger.debug(f"Making {method} request to {url} (attempt {attempt + 1})")
                
                response = await self.client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json,
                    data=data
                )
                
                # Log response
                logger.debug(
                    f"{method} {url} - {response.status_code} - {response.elapsed.total_seconds():.3f}s"
                )
                
                # Raise for HTTP errors
                response.raise_for_status()
                
                return response
                
            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP error {e.response.status_code} for {method} {url}")
                if e.response.status_code < 500 or attempt == self.retries:
                    # Don't retry client errors or if max retries reached
                    raise
                last_exception = e
                
            except (httpx.RequestError, httpx.TimeoutException) as e:
                logger.warning(f"Request error for {method} {url}: {e}")
                if attempt == self.retries:
                    raise
                last_exception = e
            
            # Exponential backoff
            if attempt < self.retries:
                wait_time = 2 ** attempt
                logger.debug(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
        
        # If we get here, all retries failed
        raise last_exception
    
    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make GET request"""
        response = await self._make_request(
            method="GET",
            path=path,
            params=params,
            headers=headers,
            correlation_id=correlation_id
        )
        return response.json()
    
    async def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make POST request"""
        response = await self._make_request(
            method="POST",
            path=path,
            json=json,
            data=data,
            headers=headers,
            correlation_id=correlation_id
        )
        return response.json()
    
    async def put(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make PUT request"""
        response = await self._make_request(
            method="PUT",
            path=path,
            json=json,
            data=data,
            headers=headers,
            correlation_id=correlation_id
        )
        return response.json()
    
    async def delete(
        self,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make DELETE request"""
        response = await self._make_request(
            method="DELETE",
            path=path,
            headers=headers,
            correlation_id=correlation_id
        )
        return response.json() if response.content else {}
    
    async def health_check(self) -> bool:
        """Check if service is healthy"""
        try:
            await self.get("/health")
            return True
        except Exception as e:
            logger.warning(f"Health check failed for {self.service_name}: {e}")
            return False


class ServiceRegistry:
    """Registry for managing service clients"""
    
    def __init__(self, config: BaseServiceConfig):
        self.config = config
        self.clients: Dict[str, ServiceClient] = {}
    
    def get_client(self, service_name: str) -> ServiceClient:
        """Get or create service client"""
        if service_name not in self.clients:
            service_urls = {
                "subject-service": self.config.subject_service_url,
                "syllabus-service": self.config.syllabus_service_url,
                "file-service": self.config.file_service_url,
                "config-service": self.config.config_service_url,
                "api-gateway": self.config.api_gateway_url,
            }
            
            base_url = service_urls.get(service_name)
            if not base_url:
                raise ValueError(f"Unknown service: {service_name}")
            
            self.clients[service_name] = ServiceClient(
                service_name=service_name,
                base_url=base_url
            )
        
        return self.clients[service_name]
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all registered services"""
        results = {}
        
        for service_name, client in self.clients.items():
            results[service_name] = await client.health_check()
        
        return results
    
    async def close_all(self):
        """Close all service clients"""
        for client in self.clients.values():
            await client.client.aclose()


# Convenience functions for common service operations
async def call_subject_service(
    method: str,
    path: str,
    config: BaseServiceConfig,
    correlation_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Call subject service"""
    async with ServiceClient("subject-service", config.subject_service_url) as client:
        if method.upper() == "GET":
            return await client.get(path, correlation_id=correlation_id, **kwargs)
        elif method.upper() == "POST":
            return await client.post(path, correlation_id=correlation_id, **kwargs)
        elif method.upper() == "PUT":
            return await client.put(path, correlation_id=correlation_id, **kwargs)
        elif method.upper() == "DELETE":
            return await client.delete(path, correlation_id=correlation_id, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")


async def call_file_service(
    method: str,
    path: str,
    config: BaseServiceConfig,
    correlation_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Call file service"""
    async with ServiceClient("file-service", config.file_service_url) as client:
        if method.upper() == "GET":
            return await client.get(path, correlation_id=correlation_id, **kwargs)
        elif method.upper() == "POST":
            return await client.post(path, correlation_id=correlation_id, **kwargs)
        elif method.upper() == "PUT":
            return await client.put(path, correlation_id=correlation_id, **kwargs)
        elif method.upper() == "DELETE":
            return await client.delete(path, correlation_id=correlation_id, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")


async def call_config_service(
    method: str,
    path: str,
    config: BaseServiceConfig,
    correlation_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Call configuration service"""
    async with ServiceClient("config-service", config.config_service_url) as client:
        if method.upper() == "GET":
            return await client.get(path, correlation_id=correlation_id, **kwargs)
        elif method.upper() == "POST":
            return await client.post(path, correlation_id=correlation_id, **kwargs)
        elif method.upper() == "PUT":
            return await client.put(path, correlation_id=correlation_id, **kwargs)
        elif method.upper() == "DELETE":
            return await client.delete(path, correlation_id=correlation_id, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")