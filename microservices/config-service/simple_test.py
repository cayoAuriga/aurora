#!/usr/bin/env python3
"""
Simple validation test for Configuration Service structure
"""
import os
import sys

def test_service_structure():
    """Test that all required files and directories exist"""
    print("🧪 Testing Configuration Service structure...")
    
    base_dir = os.path.dirname(__file__)
    
    # Required files and directories
    required_items = [
        "main.py",
        "models/__init__.py",
        "models/configuration.py", 
        "models/feature_flag.py",
        "schemas/__init__.py",
        "schemas/configuration.py",
        "schemas/feature_flag.py",
        "repositories/__init__.py",
        "repositories/configuration_repository.py",
        "repositories/feature_flag_repository.py",
        "services/__init__.py",
        "services/configuration_service.py",
        "services/feature_flag_service.py",
        "routers/__init__.py",
        "routers/configuration_router.py",
        "routers/feature_flag_router.py",
        "tests/test_configuration_service.py",
        "tests/test_feature_flag_service.py",
        "tests/test_integration.py",
        "requirements.txt",
        "README.md",
        ".env.example"
    ]
    
    missing_items = []
    
    for item in required_items:
        item_path = os.path.join(base_dir, item)
        if not os.path.exists(item_path):
            missing_items.append(item)
        else:
            print(f"   ✅ {item}")
    
    if missing_items:
        print(f"\n❌ Missing items:")
        for item in missing_items:
            print(f"   - {item}")
        return False
    
    print(f"\n🎉 All {len(required_items)} required items found!")
    return True

def test_python_syntax():
    """Test that Python files have valid syntax"""
    print("\n🧪 Testing Python syntax...")
    
    base_dir = os.path.dirname(__file__)
    
    python_files = [
        "main.py",
        "models/configuration.py",
        "models/feature_flag.py", 
        "schemas/configuration.py",
        "schemas/feature_flag.py",
        "repositories/configuration_repository.py",
        "repositories/feature_flag_repository.py",
        "services/configuration_service.py",
        "services/feature_flag_service.py",
        "routers/configuration_router.py",
        "routers/feature_flag_router.py"
    ]
    
    syntax_errors = []
    
    for py_file in python_files:
        file_path = os.path.join(base_dir, py_file)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                compile(content, file_path, 'exec')
                print(f"   ✅ {py_file}")
            except SyntaxError as e:
                syntax_errors.append(f"{py_file}: {e}")
                print(f"   ❌ {py_file}: {e}")
        else:
            print(f"   ⚠️  {py_file}: File not found")
    
    if syntax_errors:
        print(f"\n❌ Syntax errors found:")
        for error in syntax_errors:
            print(f"   - {error}")
        return False
    
    print(f"\n🎉 All Python files have valid syntax!")
    return True

def main():
    """Run all tests"""
    print("🚀 Configuration Service Validation Tests")
    print("=" * 50)
    
    structure_ok = test_service_structure()
    syntax_ok = test_python_syntax()
    
    print("\n" + "=" * 50)
    if structure_ok and syntax_ok:
        print("🎉 All tests passed! Configuration Service is ready.")
        return True
    else:
        print("❌ Some tests failed. Please check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)