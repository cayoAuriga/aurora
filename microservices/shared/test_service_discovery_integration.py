#!/usr/bin/env python3
"""
Integration test for service discovery functionality
"""
import asyncio
import sys
import time
from service_discovery import (
    ServiceRegistry,
    ServiceDiscoveryClient,
    ServiceInfo,
    get_service_registry,
    get_discovery_client
)
from health_checks import create_standard_health_checks


async def test_service_discovery_integration():
    """Test service discovery integration"""
    print("🧪 Testing Service Discovery Integration...")
    
    # Test 1: Service Registration
    print("\n📍 Test 1: Service Registration")
    registry = get_service_registry()
    discovery_client = get_discovery_client()
    
    # Register multiple services
    services_to_register = [
        ("config-service", "localhost", 8004),
        ("api-gateway", "localhost", 8000),
        ("subject-service", "localhost", 8002)
    ]
    
    for service_name, host, port in services_to_register:
        success = await discovery_client.register_self(
            service_name=service_name,
            host=host,
            port=port,
            metadata={"version": "1.0.0", "test": True}
        )
        if success:
            print(f"   ✅ Registered {service_name} at {host}:{port}")
        else:
            print(f"   ❌ Failed to register {service_name}")
            return False
    
    # Test 2: Service Discovery
    print("\n📍 Test 2: Service Discovery")
    for service_name, host, port in services_to_register:
        base_url = await discovery_client.discover_service(service_name)
        expected_url = f"http://{host}:{port}"
        if base_url == expected_url:
            print(f"   ✅ Discovered {service_name}: {base_url}")
        else:
            print(f"   ❌ Failed to discover {service_name}, got: {base_url}")
            return False
    
    # Test 3: Service Listing
    print("\n📍 Test 3: Service Listing")
    all_services = await registry.get_all_services()
    if len(all_services) == 3:
        print(f"   ✅ Found {len(all_services)} registered services")
        for service in all_services:
            print(f"      - {service.service_name} ({service.base_url})")
    else:
        print(f"   ❌ Expected 3 services, found {len(all_services)}")
        return False
    
    # Test 4: Heartbeat Updates
    print("\n📍 Test 4: Heartbeat Updates")
    for service_name, _, _ in services_to_register:
        success = await discovery_client.send_heartbeat(service_name)
        if success:
            print(f"   ✅ Heartbeat sent for {service_name}")
        else:
            print(f"   ❌ Failed to send heartbeat for {service_name}")
            return False
    
    # Test 5: Healthy Services
    print("\n📍 Test 5: Healthy Services")
    healthy_services = await registry.get_healthy_services()
    if len(healthy_services) == 3:
        print(f"   ✅ All {len(healthy_services)} services are healthy")
    else:
        print(f"   ❌ Expected 3 healthy services, found {len(healthy_services)}")
        return False
    
    # Test 6: Stale Service Cleanup
    print("\n📍 Test 6: Stale Service Cleanup")
    # Make one service stale
    service = await registry.get_service("config-service")
    if service:
        service.last_heartbeat = time.time() - 120  # 2 minutes ago
        
        cleaned_count = await registry.cleanup_stale_services(timeout_seconds=60)
        if cleaned_count == 1:
            print(f"   ✅ Cleaned up {cleaned_count} stale service")
        else:
            print(f"   ❌ Expected to clean 1 service, cleaned {cleaned_count}")
            return False
    
    # Test 7: Service Deregistration
    print("\n📍 Test 7: Service Deregistration")
    remaining_services = await registry.get_all_services()
    for service in remaining_services:
        success = await registry.deregister_service(service.service_name)
        if success:
            print(f"   ✅ Deregistered {service.service_name}")
        else:
            print(f"   ❌ Failed to deregister {service.service_name}")
            return False
    
    # Verify all services are gone
    final_services = await registry.get_all_services()
    if len(final_services) == 0:
        print("   ✅ All services successfully deregistered")
    else:
        print(f"   ❌ Expected 0 services, found {len(final_services)}")
        return False
    
    print("\n🎉 All service discovery tests passed!")
    return True


async def test_health_checks_integration():
    """Test health checks integration"""
    print("\n🧪 Testing Health Checks Integration...")
    
    # Test 1: Create Health Check Manager
    print("\n📍 Test 1: Health Check Manager Creation")
    manager = create_standard_health_checks("test-service")
    
    if len(manager.checks) >= 3:  # database, memory, disk
        print(f"   ✅ Created health manager with {len(manager.checks)} checks")
        for check_name in manager.checks:
            print(f"      - {check_name}")
    else:
        print(f"   ❌ Expected at least 3 checks, found {len(manager.checks)}")
        return False
    
    # Test 2: Run Individual Checks
    print("\n📍 Test 2: Individual Health Checks")
    for check_name in list(manager.checks.keys())[:2]:  # Test first 2 checks
        try:
            result = await manager.run_check(check_name, use_cache=False)
            if result:
                print(f"   ✅ {check_name}: {result.status.value} ({result.duration_ms:.1f}ms)")
            else:
                print(f"   ❌ {check_name}: No result")
        except Exception as e:
            print(f"   ⚠️  {check_name}: Exception - {e}")
    
    # Test 3: Overall Health Status
    print("\n📍 Test 3: Overall Health Status")
    try:
        health_status = await manager.get_overall_health(use_cache=False)
        
        print(f"   ✅ Overall Status: {health_status['status']}")
        print(f"   📊 Summary:")
        summary = health_status['summary']
        print(f"      - Total checks: {summary['total_checks']}")
        print(f"      - Healthy: {summary['healthy_checks']}")
        print(f"      - Unhealthy: {summary['unhealthy_checks']}")
        print(f"      - Degraded: {summary['degraded_checks']}")
        print(f"      - Total duration: {summary['total_duration_ms']:.1f}ms")
        
    except Exception as e:
        print(f"   ❌ Overall health check failed: {e}")
        return False
    
    print("\n🎉 All health check tests passed!")
    return True


async def main():
    """Run all integration tests"""
    print("🚀 Service Discovery & Health Checks Integration Tests")
    print("=" * 60)
    
    try:
        # Test service discovery
        discovery_success = await test_service_discovery_integration()
        
        # Test health checks
        health_success = await test_health_checks_integration()
        
        print("\n" + "=" * 60)
        if discovery_success and health_success:
            print("🎉 All integration tests passed!")
            return True
        else:
            print("❌ Some integration tests failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Integration tests failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        try:
            from service_discovery import cleanup_discovery
            await cleanup_discovery()
        except:
            pass


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)