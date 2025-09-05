"""
Tests for health check functionality
"""
import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock

from ..health_checks import (
    HealthStatus,
    HealthCheckResult,
    HealthCheck,
    HealthCheckManager,
    database_health_check,
    memory_health_check,
    disk_health_check,
    create_standard_health_checks
)


class TestHealthCheckResult:
    """Test HealthCheckResult dataclass"""
    
    def test_health_check_result_creation(self):
        """Test HealthCheckResult creation"""
        result = HealthCheckResult(
            name="test_check",
            status=HealthStatus.HEALTHY,
            message="All good",
            details={"key": "value"}
        )
        
        assert result.name == "test_check"
        assert result.status == HealthStatus.HEALTHY
        assert result.message == "All good"
        assert result.details == {"key": "value"}
        assert result.timestamp > 0
    
    def test_health_check_result_to_dict(self):
        """Test conversion to dictionary"""
        result = HealthCheckResult(
            name="test_check",
            status=HealthStatus.HEALTHY,
            message="All good"
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["name"] == "test_check"
        assert result_dict["status"] == "healthy"
        assert result_dict["message"] == "All good"
        assert "timestamp" in result_dict
        assert "duration_ms" in result_dict


class TestHealthCheck:
    """Test HealthCheck class"""
    
    @pytest.mark.asyncio
    async def test_health_check_success_boolean(self):
        """Test health check with boolean return"""
        def check_func():
            return True
        
        health_check = HealthCheck("test_check", check_func)
        result = await health_check.execute()
        
        assert result.name == "test_check"
        assert result.status == HealthStatus.HEALTHY
        assert result.message == "Check passed"
        assert result.duration_ms > 0
    
    @pytest.mark.asyncio
    async def test_health_check_failure_boolean(self):
        """Test health check with boolean failure"""
        def check_func():
            return False
        
        health_check = HealthCheck("test_check", check_func)
        result = await health_check.execute()
        
        assert result.name == "test_check"
        assert result.status == HealthStatus.UNHEALTHY
        assert result.message == "Check failed"
    
    @pytest.mark.asyncio
    async def test_health_check_dict_return(self):
        """Test health check with dictionary return"""
        def check_func():
            return {
                "status": HealthStatus.DEGRADED,
                "message": "Performance degraded",
                "details": {"cpu_usage": 85}
            }
        
        health_check = HealthCheck("test_check", check_func)
        result = await health_check.execute()
        
        assert result.name == "test_check"
        assert result.status == HealthStatus.DEGRADED
        assert result.message == "Performance degraded"
        assert result.details["cpu_usage"] == 85
    
    @pytest.mark.asyncio
    async def test_health_check_exception(self):
        """Test health check with exception"""
        def check_func():
            raise ValueError("Something went wrong")
        
        health_check = HealthCheck("test_check", check_func)
        result = await health_check.execute()
        
        assert result.name == "test_check"
        assert result.status == HealthStatus.UNHEALTHY
        assert "Something went wrong" in result.message
        assert result.details["error"] == "Something went wrong"
    
    @pytest.mark.asyncio
    async def test_health_check_timeout(self):
        """Test health check timeout"""
        async def slow_check():
            await asyncio.sleep(2)
            return True
        
        health_check = HealthCheck("test_check", slow_check, timeout_seconds=0.1)
        result = await health_check.execute()
        
        assert result.name == "test_check"
        assert result.status == HealthStatus.UNHEALTHY
        assert "timed out" in result.message
    
    @pytest.mark.asyncio
    async def test_health_check_async_function(self):
        """Test health check with async function"""
        async def async_check():
            await asyncio.sleep(0.01)
            return True
        
        health_check = HealthCheck("test_check", async_check)
        result = await health_check.execute()
        
        assert result.name == "test_check"
        assert result.status == HealthStatus.HEALTHY
        assert result.duration_ms > 0


class TestHealthCheckManager:
    """Test HealthCheckManager class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.manager = HealthCheckManager("test-service")
    
    def test_add_check(self):
        """Test adding health check"""
        def check_func():
            return True
        
        health_check = HealthCheck("test_check", check_func)
        self.manager.add_check(health_check)
        
        assert "test_check" in self.manager.checks
        assert self.manager.checks["test_check"] == health_check
    
    def test_remove_check(self):
        """Test removing health check"""
        def check_func():
            return True
        
        health_check = HealthCheck("test_check", check_func)
        self.manager.add_check(health_check)
        self.manager.remove_check("test_check")
        
        assert "test_check" not in self.manager.checks
    
    @pytest.mark.asyncio
    async def test_run_check(self):
        """Test running individual check"""
        def check_func():
            return True
        
        health_check = HealthCheck("test_check", check_func)
        self.manager.add_check(health_check)
        
        result = await self.manager.run_check("test_check")
        
        assert result is not None
        assert result.name == "test_check"
        assert result.status == HealthStatus.HEALTHY
    
    @pytest.mark.asyncio
    async def test_run_check_not_found(self):
        """Test running non-existent check"""
        result = await self.manager.run_check("non_existent")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_run_all_checks(self):
        """Test running all checks"""
        def check1():
            return True
        
        def check2():
            return False
        
        self.manager.add_check(HealthCheck("check1", check1))
        self.manager.add_check(HealthCheck("check2", check2))
        
        results = await self.manager.run_all_checks()
        
        assert len(results) == 2
        assert "check1" in results
        assert "check2" in results
        assert results["check1"].status == HealthStatus.HEALTHY
        assert results["check2"].status == HealthStatus.UNHEALTHY
    
    @pytest.mark.asyncio
    async def test_get_overall_health_healthy(self):
        """Test overall health when all checks are healthy"""
        def check1():
            return True
        
        def check2():
            return True
        
        self.manager.add_check(HealthCheck("check1", check1, critical=True))
        self.manager.add_check(HealthCheck("check2", check2, critical=False))
        
        health_status = await self.manager.get_overall_health()
        
        assert health_status["status"] == "healthy"
        assert health_status["service"] == "test-service"
        assert health_status["summary"]["total_checks"] == 2
        assert health_status["summary"]["healthy_checks"] == 2
        assert health_status["summary"]["unhealthy_checks"] == 0
    
    @pytest.mark.asyncio
    async def test_get_overall_health_unhealthy_critical(self):
        """Test overall health when critical check fails"""
        def check1():
            return False  # Critical check fails
        
        def check2():
            return True
        
        self.manager.add_check(HealthCheck("check1", check1, critical=True))
        self.manager.add_check(HealthCheck("check2", check2, critical=False))
        
        health_status = await self.manager.get_overall_health()
        
        assert health_status["status"] == "unhealthy"
        assert health_status["summary"]["unhealthy_checks"] == 1
    
    @pytest.mark.asyncio
    async def test_get_overall_health_degraded_non_critical(self):
        """Test overall health when non-critical check fails"""
        def check1():
            return True
        
        def check2():
            return False  # Non-critical check fails
        
        self.manager.add_check(HealthCheck("check1", check1, critical=True))
        self.manager.add_check(HealthCheck("check2", check2, critical=False))
        
        health_status = await self.manager.get_overall_health()
        
        assert health_status["status"] == "degraded"
    
    @pytest.mark.asyncio
    async def test_caching(self):
        """Test result caching"""
        call_count = 0
        
        def check_func():
            nonlocal call_count
            call_count += 1
            return True
        
        health_check = HealthCheck("test_check", check_func)
        self.manager.add_check(health_check)
        
        # Run check twice with caching
        await self.manager.run_check("test_check", use_cache=True)
        await self.manager.run_check("test_check", use_cache=True)
        
        # Function should only be called once due to caching
        assert call_count == 1


class TestHealthCheckFunctions:
    """Test individual health check functions"""
    
    @pytest.mark.asyncio
    async def test_database_health_check_success(self):
        """Test database health check success"""
        with patch('microservices.shared.health_checks.async_health_check') as mock_check:
            mock_check.return_value = True
            
            result = await database_health_check("test-service")
            
            assert result["status"] == HealthStatus.HEALTHY
            assert "successful" in result["message"]
    
    @pytest.mark.asyncio
    async def test_database_health_check_failure(self):
        """Test database health check failure"""
        with patch('microservices.shared.health_checks.async_health_check') as mock_check:
            mock_check.return_value = False
            
            result = await database_health_check("test-service")
            
            assert result["status"] == HealthStatus.UNHEALTHY
            assert "failed" in result["message"]
    
    @pytest.mark.asyncio
    async def test_database_health_check_exception(self):
        """Test database health check with exception"""
        with patch('microservices.shared.health_checks.async_health_check') as mock_check:
            mock_check.side_effect = Exception("Connection error")
            
            result = await database_health_check("test-service")
            
            assert result["status"] == HealthStatus.UNHEALTHY
            assert "Connection error" in result["message"]
    
    def test_memory_health_check_normal(self):
        """Test memory health check with normal usage"""
        with patch('psutil.Process') as mock_process:
            mock_memory_info = Mock()
            mock_memory_info.rss = 100 * 1024 * 1024  # 100MB
            mock_process.return_value.memory_info.return_value = mock_memory_info
            
            result = memory_health_check(max_memory_mb=500)
            
            assert result["status"] == HealthStatus.HEALTHY
            assert "normal" in result["message"]
            assert result["details"]["memory_mb"] == 100.0
    
    def test_memory_health_check_high(self):
        """Test memory health check with high usage"""
        with patch('psutil.Process') as mock_process:
            mock_memory_info = Mock()
            mock_memory_info.rss = 600 * 1024 * 1024  # 600MB
            mock_process.return_value.memory_info.return_value = mock_memory_info
            
            result = memory_health_check(max_memory_mb=500)
            
            assert result["status"] == HealthStatus.DEGRADED
            assert "High memory usage" in result["message"]
    
    def test_memory_health_check_no_psutil(self):
        """Test memory health check without psutil"""
        with patch('microservices.shared.health_checks.psutil', None):
            result = memory_health_check()
            
            assert result["status"] == HealthStatus.UNKNOWN
            assert "psutil not available" in result["message"]
    
    def test_disk_health_check_normal(self):
        """Test disk health check with normal usage"""
        with patch('psutil.disk_usage') as mock_disk_usage:
            mock_usage = Mock()
            mock_usage.total = 1000 * 1024 * 1024 * 1024  # 1TB
            mock_usage.used = 500 * 1024 * 1024 * 1024   # 500GB (50%)
            mock_usage.free = 500 * 1024 * 1024 * 1024   # 500GB
            mock_disk_usage.return_value = mock_usage
            
            result = disk_health_check(max_usage_percent=90)
            
            assert result["status"] == HealthStatus.HEALTHY
            assert "normal" in result["message"]
            assert result["details"]["usage_percent"] == 50.0
    
    def test_disk_health_check_high(self):
        """Test disk health check with high usage"""
        with patch('psutil.disk_usage') as mock_disk_usage:
            mock_usage = Mock()
            mock_usage.total = 1000 * 1024 * 1024 * 1024  # 1TB
            mock_usage.used = 950 * 1024 * 1024 * 1024   # 950GB (95%)
            mock_usage.free = 50 * 1024 * 1024 * 1024    # 50GB
            mock_disk_usage.return_value = mock_usage
            
            result = disk_health_check(max_usage_percent=90)
            
            assert result["status"] == HealthStatus.DEGRADED
            assert "High disk usage" in result["message"]


class TestCreateStandardHealthChecks:
    """Test standard health check creation"""
    
    def test_create_standard_health_checks(self):
        """Test creating standard health checks"""
        manager = create_standard_health_checks("test-service")
        
        assert isinstance(manager, HealthCheckManager)
        assert manager.service_name == "test-service"
        
        # Should have standard checks
        assert "database" in manager.checks
        assert "memory" in manager.checks
        assert "disk" in manager.checks
        
        # Database check should be critical
        assert manager.checks["database"].critical is True
        
        # Memory and disk checks should be non-critical
        assert manager.checks["memory"].critical is False
        assert manager.checks["disk"].critical is False


if __name__ == "__main__":
    pytest.main([__file__])