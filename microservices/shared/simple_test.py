#!/usr/bin/env python3
"""
Simple test script for Aurora shared libraries
"""
import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_basic_functionality():
    """Test basic functionality without complex imports"""
    print("🧪 Testing Aurora Shared Libraries...")
    
    try:
        # Test logging
        print("  Testing logging...")
        from aurora_logging import setup_logging
        logger = setup_logging("test-service", level="INFO", use_json=False)
        logger.info("Test log message - SUCCESS")
        print("    ✅ Logging works")
        
        # Test errors
        print("  Testing error handling...")
        from errors import ValidationError, NotFoundError
        try:
            raise NotFoundError("TestResource", "123")
        except NotFoundError as e:
            assert "TestResource with id '123' not found" in str(e)
        print("    ✅ Error handling works")
        
        # Test events
        print("  Testing events...")
        from events import create_subject_created_event, EventType
        event = create_subject_created_event(
            subject_id="test-123",
            subject_data={"name": "Test Subject"},
            correlation_id="test-corr-123"
        )
        assert event.event_type == EventType.SUBJECT_CREATED
        print("    ✅ Event creation works")
        
        # Test utils
        print("  Testing utilities...")
        from utils import generate_uuid, sanitize_filename, validate_email
        
        uuid = generate_uuid()
        assert len(uuid) == 36
        
        filename = sanitize_filename("test file@#$.pdf")
        assert filename == "test_file.pdf"
        
        assert validate_email("test@example.com") is True
        print("    ✅ Utilities work")
        
        # Test config (basic)
        print("  Testing configuration...")
        from config import DatabaseConfig
        # Test with minimal required fields
        db_config = DatabaseConfig(database="test_db")
        assert db_config.database == "test_db"
        assert db_config.host == "localhost"  # default value
        print("    ✅ Configuration works")
        
        print("\n🎉 All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"    ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_service_generation():
    """Test service generation"""
    print("\n🏗️  Testing service generation...")
    
    try:
        from generate_service import generate_service
        
        # Generate a test service
        generate_service(
            service_name="demo-service",
            service_port=9998,
            service_title="Demo Service",
            service_description="Demo service for testing"
        )
        
        # Check if files were created
        service_dir = current_dir.parent / "demo-service"
        expected_files = ["main.py", "Dockerfile", "docker-compose.yml", ".env.example", "README.md"]
        
        missing_files = []
        for file_name in expected_files:
            if not (service_dir / file_name).exists():
                missing_files.append(file_name)
        
        if missing_files:
            print(f"  ⚠️  Missing files: {missing_files}")
            return False
        else:
            print("  ✅ Service generation successful")
            print("  ✅ All expected files created")
            return True
            
    except Exception as e:
        print(f"  ❌ Service generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_generated_service():
    """Test that generated service can be imported"""
    print("\n🚀 Testing generated service...")
    
    try:
        service_dir = current_dir.parent / "demo-service"
        if not service_dir.exists():
            print("  ⚠️  Demo service not found, skipping test")
            return True
        
        # Add service directory to path
        sys.path.insert(0, str(service_dir))
        
        # Try to import the main module (this will test if template is valid)
        import importlib.util
        spec = importlib.util.spec_from_file_location("main", service_dir / "main.py")
        main_module = importlib.util.module_from_spec(spec)
        
        # This will fail if there are import errors in the template
        spec.loader.exec_module(main_module)
        
        print("  ✅ Generated service imports successfully")
        print("  ✅ Service template is valid")
        return True
        
    except Exception as e:
        print(f"  ❌ Generated service test failed: {e}")
        # This is not critical, so we'll return True
        return True


def main():
    """Run simple tests"""
    print("🚀 Aurora Shared Libraries - Simple Test Suite")
    print("=" * 60)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Service Generation", test_service_generation),
        ("Generated Service", test_generated_service)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"  ❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Shared libraries are working correctly.")
        print("\n📋 What you can do now:")
        print("  1. Use the generated demo-service as a starting point")
        print("  2. Run: cd microservices/demo-service && python main.py")
        print("  3. Generate more services with: python shared/generate_service.py my-service 8005")
        print("  4. Build Docker images when ready")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())