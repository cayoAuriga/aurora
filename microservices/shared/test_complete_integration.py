#!/usr/bin/env python3
"""
Complete integration test suite for service discovery and health checks
This script tests all aspects of task 2.2 implementation
"""
import asyncio
import sys
import time
import json
from typing import Dict, Any, List
from service_discovery import (
    ServiceRegistry,
    ServiceDiscoveryClient,
    ConfigurationClient,
    ServiceInfo,
    get_service_registry,
    get_discovery_client,
    get_config_client
)
from health_checks import create_standard_health_checks, HealthStatus
from config_loader import ConfigurationManager, ServiceConfig
from config_schemas import (
    ServiceRegistrationRequest,
    HealthCheckRequest,
    ConfigurationValueRequest,
    FeatureFlagCheckRequest,
    ConfigurationValidator,
    StandardConfigKeys,
    StandardFeatureFlags
)


class IntegrationTestRunner:
    """Comprehensive integration test runner"""
    
    def __init__(self):
        self.registry = get_service_registry()
        self.discovery_client = get_discovery_client()
        self.config_client = get_config_client()
        self.config_manager = ConfigurationManager()
        self.test_results = []
        self.services_registered = []
    
    async def run_all_tests(self) -> bool:
        """Run all integration tests"""
        print("🚀 Starting Complete Service Discovery & Health Check Integration Tests")
        print("=" * 80)
        
        try:
            # Test 1: Service Registry Functionality
            await self.test_service_registry_functionality()
            
            # Test 2: Service Discovery Operations
            await self.test_service_discovery_operations()
            
            # Test 3: Health Check System
            await self.test_health_check_system()
            
            # Test 4: Configuration Schemas Validation
            await self.test_configuration_schemas()
            
            # Test 5: Configuration Loading Utilities
            await self.test_configuration_loading()
            
            # Test 6: Integration with Config Service
            await self.test_config_service_integration()
            
            # Test 7: End-to-End Workflow
            await self.test_end_to_end_workflow()
            
            # Print summary
            self.print_test_summary()
            
            return all(result["passed"] for result in self.test_results)
            
        except Exception as e:
            print(f"\n❌ Integration tests failed with exception: {e}")
            import traceback
            traceba