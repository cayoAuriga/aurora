"""
Enhanced health check system for Aurora microservices
"""
import asyncio
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health check status enumeration"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    name: str
    status: HealthStatus
    message: str = ""
    details: Dict[str, Any] = None
    duration_ms: float = 0.0
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.timestamp == 0.0:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp
        }


class HealthCheck:
    """Individual health check definition"""
    
    def __init__(
        self,
        name: str,
        check_func: Callable[[], Any],
        timeout_seconds: float = 5.0,
        critical: bool = True
    ):
        self.name = name
        self.check_func = check_func
        self.timeout_seconds = timeout_seconds
        self.critical = critical
    
    async def execute(self) -> HealthCheckResult:
        """Execute the health check"""
        start_time = time.time()
        
        try:
            # Run the check with timeout
            if asyncio.iscoroutinefunction(self.check_func):
                result = await asyncio.wait_for(
                    self.check_func(),
                    timeout=self.timeout_seconds
                )
            else:
                result = await asyncio.wait_for(
                    asyncio.to_thread(self.check_func),
                    timeout=self.timeout_seconds
                )
            
            duration_ms = (time.time() - start_time) * 1000
            
            # Interpret result
            if isinstance(result, bool):
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                message = "Check passed" if result else "Check failed"
                details = {}
            elif isinstance(result, dict):
                status = HealthStatus(result.get("status", HealthStatus.HEALTHY))
                message = result.get("message", "")
                details = result.get("details", {})
            else:
                status = HealthStatus.HEALTHY
                message = str(result)
                details = {"result": result}
            
            return HealthCheckResult(
                name=self.name,
                status=status,
                message=message,
                details=details,
                duration_ms=duration_ms
            )
            
        except asyncio.TimeoutError:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check timed out after {self.timeout_seconds}s",
                duration_ms=duration_ms
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                details={"error": str(e), "error_type": type(e).__name__},
                duration_ms=duration_ms
            )


class HealthCheckManager:
    """Manages multiple health checks for a service"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.checks: Dict[str, HealthCheck] = {}
        self._last_results: Dict[str, HealthCheckResult] = {}
        self._cache_ttl = 30  # Cache results for 30 seconds
    
    def add_check(self, health_check: HealthCheck):
        """Add a health check"""
        self.checks[health_check.name] = health_check
        logger.info(f"Added health check: {health_check.name}")
    
    def remove_check(self, name: str):
        """Remove a health check"""
        if name in self.checks:
            del self.checks[name]
            if name in self._last_results:
                del self._last_results[name]
            logger.info(f"Removed health check: {name}")
    
    async def run_check(self, name: str, use_cache: bool = True) -> Optional[HealthCheckResult]:
        """Run a specific health check"""
        if name not in self.checks:
            return None
        
        # Check cache
        if use_cache and name in self._last_results:
            last_result = self._last_results[name]
            if (time.time() - last_result.timestamp) < self._cache_ttl:
                return last_result
        
        # Run the check
        result = await self.checks[name].execute()
        self._last_results[name] = result
        return result
    
    async def run_all_checks(self, use_cache: bool = True) -> Dict[str, HealthCheckResult]:
        """Run all health checks"""
        results = {}
        
        # Run checks concurrently
        tasks = []
        for name in self.checks:
            tasks.append(self.run_check(name, use_cache))
        
        check_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, name in enumerate(self.checks):
            result = check_results[i]
            if isinstance(result, Exception):
                result = HealthCheckResult(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check execution failed: {str(result)}"
                )
            results[name] = result
        
        return results
    
    async def get_overall_health(self, use_cache: bool = True) -> Dict[str, Any]:
        """Get overall service health status"""
        check_results = await self.run_all_checks(use_cache)
        
        # Determine overall status
        critical_checks = [
            result for name, result in check_results.items()
            if self.checks[name].critical
        ]
        
        non_critical_checks = [
            result for name, result in check_results.items()
            if not self.checks[name].critical
        ]
        
        # Overall status logic
        if any(check.status == HealthStatus.UNHEALTHY for check in critical_checks):
            overall_status = HealthStatus.UNHEALTHY
        elif any(check.status == HealthStatus.DEGRADED for check in critical_checks):
            overall_status = HealthStatus.DEGRADED
        elif any(check.status == HealthStatus.UNHEALTHY for check in non_critical_checks):
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY
        
        # Calculate total duration
        total_duration = sum(result.duration_ms for result in check_results.values())
        
        return {
            "service": self.service_name,
            "status": overall_status.value,
            "timestamp": time.time(),
            "checks": {name: result.to_dict() for name, result in check_results.items()},
            "summary": {
                "total_checks": len(check_results),
                "healthy_checks": len([r for r in check_results.values() if r.status == HealthStatus.HEALTHY]),
                "unhealthy_checks": len([r for r in check_results.values() if r.status == HealthStatus.UNHEALTHY]),
                "degraded_checks": len([r for r in check_results.values() if r.status == HealthStatus.DEGRADED]),
                "total_duration_ms": total_duration
            }
        }


# Common health check functions
async def database_health_check(service_name: str) -> Dict[str, Any]:
    """Standard database health check"""
    try:
        from .database import async_health_check
        is_healthy = await async_health_check(service_name)
        
        return {
            "status": HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY,
            "message": "Database connection successful" if is_healthy else "Database connection failed",
            "details": {"connection_pool": "active" if is_healthy else "inactive"}
        }
    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY,
            "message": f"Database health check failed: {str(e)}",
            "details": {"error": str(e)}
        }


def memory_health_check(max_memory_mb: int = 1000) -> Dict[str, Any]:
    """Memory usage health check"""
    try:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        if memory_mb > max_memory_mb:
            status = HealthStatus.DEGRADED
            message = f"High memory usage: {memory_mb:.1f}MB"
        else:
            status = HealthStatus.HEALTHY
            message = f"Memory usage normal: {memory_mb:.1f}MB"
        
        return {
            "status": status,
            "message": message,
            "details": {
                "memory_mb": round(memory_mb, 1),
                "max_memory_mb": max_memory_mb,
                "usage_percent": round((memory_mb / max_memory_mb) * 100, 1)
            }
        }
    except ImportError:
        return {
            "status": HealthStatus.UNKNOWN,
            "message": "psutil not available for memory monitoring"
        }
    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY,
            "message": f"Memory check failed: {str(e)}"
        }


def disk_health_check(path: str = "/", max_usage_percent: int = 90) -> Dict[str, Any]:
    """Disk usage health check"""
    try:
        import psutil
        disk_usage = psutil.disk_usage(path)
        usage_percent = (disk_usage.used / disk_usage.total) * 100
        
        if usage_percent > max_usage_percent:
            status = HealthStatus.DEGRADED
            message = f"High disk usage: {usage_percent:.1f}%"
        else:
            status = HealthStatus.HEALTHY
            message = f"Disk usage normal: {usage_percent:.1f}%"
        
        return {
            "status": status,
            "message": message,
            "details": {
                "path": path,
                "usage_percent": round(usage_percent, 1),
                "free_gb": round(disk_usage.free / 1024 / 1024 / 1024, 1),
                "total_gb": round(disk_usage.total / 1024 / 1024 / 1024, 1)
            }
        }
    except ImportError:
        return {
            "status": HealthStatus.UNKNOWN,
            "message": "psutil not available for disk monitoring"
        }
    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY,
            "message": f"Disk check failed: {str(e)}"
        }


async def service_dependency_check(service_name: str, discovery_client) -> Dict[str, Any]:
    """Check if a dependent service is available"""
    try:
        is_available = await discovery_client.health_check_service(service_name)
        
        return {
            "status": HealthStatus.HEALTHY if is_available else HealthStatus.UNHEALTHY,
            "message": f"Service {service_name} is {'available' if is_available else 'unavailable'}",
            "details": {"service_name": service_name, "available": is_available}
        }
    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY,
            "message": f"Dependency check failed for {service_name}: {str(e)}",
            "details": {"service_name": service_name, "error": str(e)}
        }


def create_standard_health_checks(service_name: str, discovery_client=None) -> HealthCheckManager:
    """Create standard health checks for a service"""
    manager = HealthCheckManager(service_name)
    
    # Database check (critical)
    async def db_check():
        return await database_health_check(service_name)
    
    manager.add_check(HealthCheck(
        name="database",
        check_func=db_check,
        timeout_seconds=5.0,
        critical=True
    ))
    
    # Memory check (non-critical)
    manager.add_check(HealthCheck(
        name="memory",
        check_func=lambda: memory_health_check(),
        timeout_seconds=2.0,
        critical=False
    ))
    
    # Disk check (non-critical)
    manager.add_check(HealthCheck(
        name="disk",
        check_func=lambda: disk_health_check(),
        timeout_seconds=2.0,
        critical=False
    ))
    
    return manager