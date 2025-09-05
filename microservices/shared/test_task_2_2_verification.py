#!/usr/bin/env python3
"""
Task 2.2 Verification: Service Discovery and Health Checks Implementation
"""
import asyncio
import sys
import time
from typing import Dict, Any

# Add the parent directory to the path to import shared modules
sys.path.insert(0, '../..')

from microservices.shared.service_discovery import (
    ServiceRegistry,
    ServiceDiscoveryClient,
    ConfigurationClient,
    ServiceInfo,
    get_service_registry,
    get_discovery_client,
    get_config_client
)
from microservices.shared.health_checks import (
    HealthCheckManager,
    HealthCheck,
    HealthStatus,
    create_standard_health_checks
)
from microservices.shared.config_loader import (
    ConfigurationManager,
    ServiceConfig,
    get_service_config
)
from microservices.shared.config_schemas import (
    ServiceRegistrationRequest,
    HealthCheckRequest,
    ConfigurationValueRequest,
    FeatureFlagCheckRequest,
    ConfigurationValidator,
    StandardConfigKeys,
    StandardFeatureFlags
)


class Task22Verifier:
    """Verifies that Task 2.2 requirements are implemented"""
    
    def __init__(self):
        self.results = []
        self.registry = ServiceRegistry()
        self.discovery_client = ServiceDiscoveryClient(self.registry)
        self.config_client = ConfigurationClient(self.discovery_client)
        self.config_manager = ConfigurationManager()
    
    def log_result(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.results.append((test_name, passed, message))
        print(f"{status} {test_name}: {message}")
    
    async def test_service_registry_functionality(self):
        """Test service registry functionality for service discovery"""
        print("\n🧪 Testing Service Registry Functionality...")
        
        try:
            # Test service registration
            service_info = ServiceInfo(
                service_name="test-service",
                host="localhost",
                port=8001,
                health_endpoint="/health/ready",
                metadata={"version": "1.0.0", "test": True}
            )
            
            success = await self.registry.register_service(service_info)
            self.log_result(
                "Service Registration", 
                success, 
                "Service can be registered in registry"
            )
            
            # Test service discovery
            registered_service = await self.registry.get_service("test-service")
            self.log_result(
                "Service Discovery", 
                registered_service is not None and registered_service.service_name == "test-service",
                "Service can be discovered from registry"
            )
            
            # Test service listing
            all_services = await self.registry.get_all_services()
            self.log_result(
                "Service Listing", 
                len(all_services) >= 1 and any(s.service_name == "test-service" for s in all_services),
                f"Registry contains {len(all_services)} services"
            )
            
            # Test healthy services filtering
            healthy_services = await self.registry.get_healthy_services()
            self.log_result(
                "Healthy Services Filter", 
                len(healthy_services) >= 1,
                f"Found {len(healthy_services)} healthy services"
            )
            
            # Test heartbeat update
            heartbeat_success = await self.registry.update_heartbeat("test-service")
            self.log_result(
                "Heartbeat Update", 
                heartbeat_success,
                "Service heartbeat can be updated"
            )
            
            # Test service deregistration
            deregister_success = await self.registry.deregister_service("test-service")
            self.log_result(
                "Service Deregistration", 
                deregister_success,
                "Service can be deregistered"
            )
            
        except Exception as e:
            self.log_result("Service Registry Functionality", False, f"Exception: {str(e)}")
    
    async def test_health_check_endpoints(self):
        """Test health check endpoints for all services"""
        print("\n🧪 Testing Health Check Endpoints...")
        
        try:
            # Test health check manager creation
            health_manager = create_standard_health_checks("test-service", self.discovery_client)
            self.log_result(
                "Health Check Manager Creation", 
                isinstance(health_manager, HealthCheckManager),
                "Standard health checks can be created"
            )
            
            # Test individual health check
            def simple_check():
                return True
            
            health_check = HealthCheck("simple_test", simple_check)
            health_manager.add_check(health_check)
            
            result = await health_manager.run_check("simple_test")
            self.log_result(
                "Individual Health Check", 
                result is not None and result.status == HealthStatus.HEALTHY,
                "Individual health checks can be executed"
            )
            
            # Test overall health status
            overall_health = await health_manager.get_overall_health()
            self.log_result(
                "Overall Health Status", 
                "status" in overall_health and "service" in overall_health,
                f"Overall health status: {overall_health.get('status', 'unknown')}"
            )
            
            # Test health check with different statuses
            def failing_check():
                return False
            
            failing_health_check = HealthCheck("failing_test", failing_check)
            health_manager.add_check(failing_health_check)
            
            failing_result = await health_manager.run_check("failing_test")
            self.log_result(
                "Failing Health Check", 
                failing_result is not None and failing_result.status == HealthStatus.UNHEALTHY,
                "Failing health checks are properly detected"
            )
            
        except Exception as e:
            self.log_result("Health Check Endpoints", False, f"Exception: {str(e)}")
    
    def test_configuration_schemas_validation(self):
        """Test shared configuration schemas and validation"""
        print("\n🧪 Testing Configuration Schemas and Validation...")
        
        try:
            # Test service registration request validation
            valid_request = ServiceRegistrationRequest(
                service_name="test-service",
                host="localhost",
                port=8000,
                health_endpoint="/health",
                metadata={"test": True}
            )
            self.log_result(
                "Service Registration Schema", 
                valid_request.service_name == "test-service",
                "Service registration request schema works"
            )
            
            # Test configuration value request validation
            config_request = ConfigurationValueRequest(
                config_key="database.pool.size",
                environment="development"
            )
            self.log_result(
                "Configuration Value Schema", 
                config_request.config_key == "database.pool.size",
                "Configuration value request schema works"
            )
            
            # Test feature flag request validation
            flag_request = FeatureFlagCheckRequest(
                flag_key="enable_new_feature",
                user_id=123
            )
            self.log_result(
                "Feature Flag Schema", 
                flag_request.flag_key == "enable_new_feature",
                "Feature flag request schema works"
            )
            
            # Test configuration validator
            validator = ConfigurationValidator()
            
            valid_service_name = validator.validate_service_name("test-service")
            self.log_result(
                "Service Name Validation", 
                valid_service_name,
                "Service name validation works"
            )
            
            valid_config_key = validator.validate_config_key("database.pool.size")
            self.log_result(
                "Config Key Validation", 
                valid_config_key,
                "Configuration key validation works"
            )
            
            valid_port = validator.validate_port(8000)
            self.log_result(
                "Port Validation", 
                valid_port,
                "Port validation works"
            )
            
        except Exception as e:
            self.log_result("Configuration Schemas Validation", False, f"Exception: {str(e)}")
    
    async def test_configuration_loading_utilities(self):
        """Test configuration loading utilities for other services"""
        print("\n🧪 Testing Configuration Loading Utilities...")
        
        try:
            # Test service config creation
            service_config = await get_service_config("test-service", load_remote=False)
            self.log_result(
                "Service Config Creation", 
                isinstance(service_config, ServiceConfig) and service_config.service_name == "test-service",
                "Service configuration can be created"
            )
            
            # Test configuration manager
            config_manager = ConfigurationManager()
            test_config = await config_manager.get_service_config("test-service", load_remote=False)
            self.log_result(
                "Configuration Manager", 
                isinstance(test_config, ServiceConfig),
                "Configuration manager works"
            )
            
            # Test configuration validation
            validation_result = await config_manager.validate_service_config("test-service")
            self.log_result(
                "Configuration Validation", 
                "valid" in validation_result and "errors" in validation_result,
                f"Configuration validation: {'valid' if validation_result.get('valid') else 'invalid'}"
            )
            
            # Test standard configuration keys
            standard_keys_exist = hasattr(StandardConfigKeys, 'LOG_LEVEL')
            self.log_result(
                "Standard Config Keys", 
                standard_keys_exist,
                "Standard configuration keys are defined"
            )
            
            # Test standard feature flags
            standard_flags_exist = hasattr(StandardFeatureFlags, 'ENABLE_DETAILED_LOGGING')
            self.log_result(
                "Standard Feature Flags", 
                standard_flags_exist,
                "Standard feature flags are defined"
            )
            
        except Exception as e:
            self.log_result("Configuration Loading Utilities", False, f"Exception: {str(e)}")
    
    async def test_service_discovery_integration(self):
        """Test service discovery integration"""
        print("\n🧪 Testing Service Discovery Integration...")
        
        try:
            # Test discovery client functionality
            success = await self.discovery_client.register_self(
                service_name="integration-test-service",
                host="localhost",
                port=8002,
                metadata={"integration_test": True}
            )
            self.log_result(
                "Discovery Client Registration", 
                success,
                "Discovery client can register services"
            )
            
            # Test service URL discovery
            service_url = await self.discovery_client.discover_service("integration-test-service")
            self.log_result(
                "Service URL Discovery", 
                service_url == "http://localhost:8002",
                f"Service URL discovered: {service_url}"
            )
            
            # Test service URL with path
            full_url = await self.discovery_client.get_service_url("integration-test-service", "/api/v1/test")
            self.log_result(
                "Service URL with Path", 
                full_url == "http://localhost:8002/api/v1/test",
                f"Full URL: {full_url}"
            )
            
            # Test heartbeat sending
            heartbeat_success = await self.discovery_client.send_heartbeat("integration-test-service")
            self.log_result(
                "Heartbeat Sending", 
                heartbeat_success,
                "Heartbeat can be sent via discovery client"
            )
            
            # Clean up
            await self.registry.deregister_service("integration-test-service")
            
        except Exception as e:
            self.log_result("Service Discovery Integration", False, f"Exception: {str(e)}")
    
    def test_global_instances(self):
        """Test global service discovery instances"""
        print("\n🧪 Testing Global Instances...")
        
        try:
            # Test global registry
            global_registry = get_service_registry()
            self.log_result(
                "Global Service Registry", 
                isinstance(global_registry, ServiceRegistry),
                "Global service registry is available"
            )
            
            # Test global discovery client
            global_discovery = get_discovery_client()
            self.log_result(
                "Global Discovery Client", 
                isinstance(global_discovery, ServiceDiscoveryClient),
                "Global discovery client is available"
            )
            
            # Test global config client
            global_config = get_config_client()
            self.log_result(
                "Global Config Client", 
                isinstance(global_config, ConfigurationClient),
                "Global configuration client is available"
            )
            
        except Exception as e:
            self.log_result("Global Instances", False, f"Exception: {str(e)}")
    
    async def run_all_tests(self):
        """Run all verification tests"""
        print("🚀 Task 2.2 Verification: Service Discovery and Health Checks")
        print("=" * 70)
        
        # Run all test methods
        await self.test_service_registry_functionality()
        await self.test_health_check_endpoints()
        self.test_configuration_schemas_validation()
        await self.test_configuration_loading_utilities()
        await self.test_service_discovery_integration()
        self.test_global_instances()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 Test Results Summary")
        print("=" * 70)
        
        passed_count = sum(1 for _, passed, _ in self.results if passed)
        total_count = len(self.results)
        
        for test_name, passed, message in self.results:
            status = "✅" if passed else "❌"
            print(f"{status} {test_name}")
            if message and not passed:
                print(f"   └─ {message}")
        
        print(f"\n🎯 Results: {passed_count}/{total_count} tests passed")
        
        if passed_count == total_count:
            print("🎉 Task 2.2 Implementation: COMPLETE")
            print("\n✅ All requirements satisfied:")
            print("   • Service registry functionality for service discovery")
            print("   • Health check endpoints for all services")
            print("   • Shared configuration schemas and validation")
            print("   • Configuration loading utilities for other services")
            print("   • Integration tests for service discovery")
        else:
            print("⚠️  Task 2.2 Implementation: INCOMPLETE")
            failed_tests = [name for name, passed, _ in self.results if not passed]
            print(f"   Failed tests: {', '.join(failed_tests)}")
        
        return passed_count == total_count


async def main():
    """Main verification function"""
    verifier = Task22Verifier()
    success = await verifier.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)