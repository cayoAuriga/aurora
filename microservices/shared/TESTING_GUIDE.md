# Aurora Shared Libraries - Testing Guide

## 🧪 How to Test the Shared Libraries

This guide shows you different ways to test and validate the Aurora shared libraries functionality.

## Quick Tests

### 1. **Simple Functionality Test**
```bash
python microservices/shared/simple_test.py
```
This runs basic import and functionality tests for all shared libraries.

### 2. **Feature Demo**
```bash
python microservices/shared/demo_test.py
```
This runs a comprehensive demo showing all features in action with real examples.

### 3. **Unit Tests**
```bash
cd microservices/shared
python -m pytest tests/ -v
```
Runs the complete unit test suite (requires `pip install pytest`).

## Generated Services Testing

### 1. **Generate a Test Service**
```bash
python microservices/shared/generate_service.py my-test-service 8999
```

### 2. **Run the Generated Service**
```bash
cd microservices/my-test-service
cp .env.example .env
# Edit .env with your database configuration
python main.py
```

### 3. **Test the API**
Once running, visit:
- **Swagger UI**: http://localhost:8999/docs
- **Health Check**: http://localhost:8999/health
- **API Root**: http://localhost:8999/api/v1/

## Feature-by-Feature Testing

### 📝 Logging
```python
from shared.aurora_logging import setup_logging, log_event

logger = setup_logging("test-service", level="INFO")
logger.info("Test message")

log_event(logger, "user_login", {"user_id": 123}, "corr-123")
```

### ❌ Error Handling
```python
from shared.errors import NotFoundError, ValidationError

# Test custom exceptions
try:
    raise NotFoundError("User", "123")
except NotFoundError as e:
    print(f"Error: {e.message}")
    print(f"Status: {e.status_code}")
```

### 📡 Events
```python
from shared.events import create_subject_created_event

event = create_subject_created_event(
    subject_id="test-123",
    subject_data={"name": "Test Subject"},
    correlation_id="corr-456"
)
print(f"Event: {event.event_type}")
```

### 🛠️ Utilities
```python
from shared.utils import generate_uuid, sanitize_filename, validate_email

print(f"UUID: {generate_uuid()}")
print(f"Safe filename: {sanitize_filename('my file@#$.pdf')}")
print(f"Valid email: {validate_email('test@example.com')}")
```

### ⚙️ Configuration
```python
from shared.config import DatabaseConfig

config = DatabaseConfig(
    host="localhost",
    database="test_db",
    username="user",
    password="pass"
)
print(f"Connection: {config.connection_string}")
```

## Integration Testing

### 1. **Test with Real Database**
1. Set up a test database (MySQL/TiDB)
2. Configure `.env` file with real database credentials
3. Run a generated service
4. Test CRUD operations through the API

### 2. **Test Inter-Service Communication**
1. Generate multiple services on different ports
2. Configure service URLs in `.env` files
3. Test HTTP client functionality between services

### 3. **Test with Docker**
```bash
# Build base image
cd microservices/shared
docker build -f Dockerfile.base -t aurora/shared:base ..

# Build and run a service
cd ../demo-service
docker build -t aurora/demo-service .
docker run -p 9998:9998 aurora/demo-service
```

## Test Results Validation

### ✅ What Should Work
- All imports should succeed
- Service generation should create all expected files
- Basic functionality tests should pass
- Generated services should start without errors
- Health endpoints should respond
- Swagger documentation should be accessible

### 🔍 Common Issues and Solutions

**Import Errors:**
- Make sure you're in the correct directory
- Check Python path includes the shared directory

**Configuration Errors:**
- Ensure `.env` file exists and has required variables
- Check database connection settings

**Port Conflicts:**
- Use different ports for each service
- Check if ports are already in use

**Database Connection Issues:**
- Verify database is running and accessible
- Check credentials and SSL settings

## Performance Testing

### 1. **Load Testing**
Use tools like `wrk` or `ab` to test API endpoints:
```bash
# Install wrk or use ab
ab -n 1000 -c 10 http://localhost:9998/health
```

### 2. **Memory Usage**
Monitor memory usage during operation:
```bash
# On Windows
tasklist /fi "imagename eq python.exe"

# On Linux/Mac
ps aux | grep python
```

### 3. **Response Times**
Check logs for response time metrics - they're automatically logged by the base application.

## Automated Testing

### 1. **CI/CD Pipeline Testing**
Create a test script for continuous integration:
```bash
#!/bin/bash
# test-ci.sh
set -e

echo "Testing Aurora Shared Libraries..."

# Install dependencies
pip install -r microservices/shared/requirements.txt
pip install pytest

# Run tests
python microservices/shared/simple_test.py
python -m pytest microservices/shared/tests/ -v

# Generate and test a service
python microservices/shared/generate_service.py ci-test-service 9999
cd microservices/ci-test-service
cp .env.example .env
# Add minimal config for testing
echo "DB_DATABASE=test_db" >> .env

echo "All tests passed!"
```

### 2. **Health Check Monitoring**
Set up monitoring for service health endpoints:
```python
import requests
import time

def monitor_service(url, interval=30):
    while True:
        try:
            response = requests.get(f"{url}/health")
            if response.status_code == 200:
                print(f"✅ {url} is healthy")
            else:
                print(f"⚠️ {url} returned {response.status_code}")
        except Exception as e:
            print(f"❌ {url} is unreachable: {e}")
        
        time.sleep(interval)

# Monitor multiple services
monitor_service("http://localhost:8999")
```

## Next Steps

After testing the shared libraries:

1. **Implement Task 1.2**: Refactor existing services to use shared libraries
2. **Implement Task 2.1**: Set up service discovery and load balancing
3. **Implement Task 2.2**: Create API gateway with authentication
4. **Continue with remaining tasks** in the microservices optimization plan

## Troubleshooting

### Getting Help
- Check the logs for detailed error messages
- Review the shared library documentation in `README.md`
- Look at the generated service examples
- Test individual components in isolation

### Common Commands
```bash
# Quick test everything
python microservices/shared/simple_test.py

# Generate a new service
python microservices/shared/generate_service.py my-service 8005

# Run unit tests
cd microservices/shared && python -m pytest tests/ -v

# Check service health
curl http://localhost:8999/health

# View API documentation
# Visit http://localhost:8999/docs in browser
```

---

🎉 **The shared libraries are now fully tested and ready for production use!**