#!/usr/bin/env python3
"""
Test runner for Aurora shared libraries
"""
import sys
import os
import subprocess
import importlib.util
from pathlib import Path

# Add shared directory to Python path
shared_dir = Path(__file__).parent
sys.path.insert(0, str(shared_dir))

def test_imports():
    """Test that all shared modules can be imported"""
    print("🧪 Testing module imports...")
    
    modules_to_test = [
        'shared.aurora_logging',
        'shared.errors', 
        'shared.events',
        'shared.config',
        'shared.database',
        'shared.base_app',
        'shared.http_client',
        'shared.utils'
    ]
    
    failed_imports = []
    
    for module_name in modules_to_test:
        try:
            # Try to import the module
            spec = importlib.util.spec_from_file_location(
                module_name, 
                shared_dir / f"{module_name.split('.')[-1]}.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"  ✅ {module_name}")
        except Exception as e:
            print(f"  ❌ {module_name}: {e}")
            failed_imports.append(module_name)
    
    return len(failed_imports) == 0


def test_service_generation():
    """Test service generation"""
    print("\n🏗️  Testing service generation...")
    
    try:
        # Generate a test service
        result = subprocess.run([
            sys.executable, 
            "generate_service.py", 
            "test-generated-service", 
            "9999",
            "--title", "Generated Test Service"
        ], 
        cwd=shared_dir,
        capture_output=True, 
        text=True
        )
        
        if result.returncode == 0:
            print("  ✅ Service generation successful")
            
            # Check if files were created
            service_dir = shared_dir.parent / "test-generated-service"
            expected_files = ["main.py", "Dockerfile", "docker-compose.yml", ".env.example", "README.md"]
            
            missing_files = []
            for file_name in expected_files:
                if not (service_dir / file_name).exists():
                    missing_files.append(file_name)
            
            if missing_files:
                print(f"  ⚠️  Missing files: {missing_files}")
                return False
            else:
                print("  ✅ All expected files created")
                return True
        else:
            print(f"  ❌ Service generation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ❌ Service generation error: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality of shared libraries"""
    print("\n⚙️  Testing basic functionality...")
    
    try:
        # Test logging
        from shared.aurora_logging import setup_logging
        logger = setup_logging("test-service", level="INFO")
        logger.info("Test log message")
        print("  ✅ Logging works")
        
        # Test errors
        from shared.errors import ValidationError, NotFoundError
        try:
            raise NotFoundError("TestResource", "123")
        except NotFoundError as e:
            assert "TestResource with id '123' not found" in str(e)
        print("  ✅ Error handling works")
        
        # Test events
        from shared.events import create_subject_created_event, EventType
        event = create_subject_created_event(
            subject_id="test-123",
            subject_data={"name": "Test Subject"},
            correlation_id="test-corr-123"
        )
        assert event.event_type == EventType.SUBJECT_CREATED
        print("  ✅ Event creation works")
        
        # Test utils
        from shared.utils import generate_uuid, sanitize_filename, validate_email
        uuid = generate_uuid()
        assert len(uuid) == 36
        
        filename = sanitize_filename("test file@#$.pdf")
        assert filename == "test_file.pdf"
        
        assert validate_email("test@example.com") is True
        print("  ✅ Utilities work")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Basic functionality test failed: {e}")
        return False


def run_unit_tests():
    """Run unit tests if pytest is available"""
    print("\n🧪 Running unit tests...")
    
    try:
        # Check if pytest is available
        result = subprocess.run([sys.executable, "-m", "pytest", "--version"], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print("  ⚠️  pytest not available, skipping unit tests")
            print("  💡 Install pytest to run unit tests: pip install pytest")
            return True
        
        # Run tests
        test_dir = shared_dir / "tests"
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            str(test_dir), 
            "-v", 
            "--tb=short"
        ], 
        cwd=shared_dir,
        capture_output=True, 
        text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print("  ✅ All unit tests passed")
            return True
        else:
            print("  ❌ Some unit tests failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Unit test execution error: {e}")
        return False


def test_docker_build():
    """Test Docker base image build"""
    print("\n🐳 Testing Docker base image build...")
    
    try:
        # Check if Docker is available
        result = subprocess.run(["docker", "--version"], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print("  ⚠️  Docker not available, skipping Docker tests")
            return True
        
        # Try to build base image
        result = subprocess.run([
            "docker", "build", 
            "-f", "Dockerfile.base",
            "-t", "aurora/shared:test",
            ".."
        ], 
        cwd=shared_dir,
        capture_output=True, 
        text=True
        )
        
        if result.returncode == 0:
            print("  ✅ Docker base image builds successfully")
            
            # Clean up test image
            subprocess.run(["docker", "rmi", "aurora/shared:test"], 
                         capture_output=True)
            return True
        else:
            print(f"  ❌ Docker build failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ❌ Docker test error: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Aurora Shared Libraries Test Suite")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Service Generation", test_service_generation),
        ("Basic Functionality", test_basic_functionality),
        ("Unit Tests", run_unit_tests),
        ("Docker Build", test_docker_build)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"  ❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
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
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())