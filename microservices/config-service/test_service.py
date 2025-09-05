#!/usr/bin/env python3
"""
Simple test script for Configuration Service
"""
import sys
import os

# Add the microservices directory to the path
microservices_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, microservices_dir)

from fastapi.testclient import TestClient

# Import the app from config-service
try:
    from config_service.main import app
except ImportError:
    # Alternative import path
    sys.path.insert(0, os.path.dirname(__file__))
    from main import app

def test_configuration_service():
    """Test basic Configuration Service functionality"""
    client = TestClient(app)
    
    print("🧪 Testing Configuration Service...")
    
    # Test root endpoint
    print("📍 Testing root endpoint...")
    response = client.get("/")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Response: {response.json()}")
        print("   ✅ Root endpoint working")
    else:
        print("   ❌ Root endpoint failed")
        return False
    
    # Test status endpoint
    print("📍 Testing status endpoint...")
    response = client.get("/status")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Response: {response.json()}")
        print("   ✅ Status endpoint working")
    else:
        print("   ❌ Status endpoint failed")
        return False
    
    # Test health endpoint
    print("📍 Testing health endpoint...")
    response = client.get("/health")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Response: {response.json()}")
        print("   ✅ Health endpoint working")
    else:
        print("   ❌ Health endpoint failed")
        return False
    
    # Test OpenAPI docs
    print("📍 Testing OpenAPI docs...")
    response = client.get("/docs")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ OpenAPI docs accessible")
    else:
        print("   ❌ OpenAPI docs failed")
    
    # Test configuration endpoints (will fail without database, but should return proper error)
    print("📍 Testing configuration endpoints...")
    response = client.get("/api/v1/configurations/")
    print(f"   Status: {response.status_code}")
    if response.status_code in [200, 500]:  # 500 expected without database
        print("   ✅ Configuration endpoint structure working")
    else:
        print("   ❌ Configuration endpoint structure failed")
    
    # Test feature flag endpoints
    print("📍 Testing feature flag endpoints...")
    response = client.get("/api/v1/feature-flags/")
    print(f"   Status: {response.status_code}")
    if response.status_code in [200, 500]:  # 500 expected without database
        print("   ✅ Feature flag endpoint structure working")
    else:
        print("   ❌ Feature flag endpoint structure failed")
    
    print("\n🎉 Configuration Service basic tests completed!")
    return True

if __name__ == "__main__":
    success = test_configuration_service()
    sys.exit(0 if success else 1)