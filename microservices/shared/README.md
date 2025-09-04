# Aurora Shared Libraries

This directory contains shared libraries and utilities for Aurora microservices.

## Structure

```
shared/
├── __init__.py              # Package initialization
├── base_app.py             # Base FastAPI application template
├── config.py               # Configuration management
├── database.py             # Database utilities and connections
├── errors.py               # Error handling and exceptions
├── events.py               # Event schemas and utilities
├── http_client.py          # Inter-service HTTP client
├── logging.py              # Logging utilities
├── utils.py                # General utility functions
├── requirements.txt        # Shared dependencies
├── Dockerfile.base         # Base Docker image
├── generate_service.py     # Service generator script
└── templates/              # Service templates
    ├── service_template.py
    ├── Dockerfile.template
    └── docker-compose.service.yml
```

## Components

### Base Application (`base_app.py`)

Provides a base FastAPI application class with:
- Standardized middleware setup
- Error handling
- Health check endpoints
- Request logging with correlation IDs
- CORS configuration

**Usage:**
```python
from shared.base_app import create_service
from shared.config import get_config

config = get_config("my-service")
service = create_service("my-service", config)
app = service.app
```

### Configuration (`config.py`)

Centralized configuration management using Pydantic settings:
- Database configuration
- Redis configuration
- Service discovery
- Inter-service URLs
- Security settings

**Usage:**
```python
from shared.config import get_config

config = get_config("subject-service")
print(config.database.connection_string)
```

### Database (`database.py`)

Database utilities and connection management:
- SQLAlchemy engine creation
- Session management
- Base repository classes
- Health checks

**Usage:**
```python
from shared.database import get_db_session, BaseRepository

# Sync usage
with get_db_session("subject-service") as db:
    # Use database session
    pass

# Repository pattern
class SubjectRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, Subject)
```

### Error Handling (`errors.py`)

Standardized error handling:
- Custom exception classes
- Error response models
- HTTP exception conversion

**Usage:**
```python
from shared.errors import NotFoundError, ValidationError

# Raise custom exceptions
raise NotFoundError("Subject", "123")
raise ValidationError("Invalid input", details=[...])
```

### Events (`events.py`)

Event-driven communication schemas:
- Domain event models
- Event types enumeration
- Event creation utilities

**Usage:**
```python
from shared.events import create_subject_created_event, EventType

event = create_subject_created_event(
    subject_id="123",
    subject_data={"name": "Math"},
    correlation_id="abc-123"
)
```

### HTTP Client (`http_client.py`)

Inter-service communication:
- Circuit breaker pattern
- Retry logic with exponential backoff
- Correlation ID propagation
- Service registry

**Usage:**
```python
from shared.http_client import ServiceClient

async with ServiceClient("subject-service", "http://localhost:8002") as client:
    subjects = await client.get("/api/v1/subjects")
```

### Logging (`logging.py`)

Structured logging:
- JSON formatting
- Correlation ID tracking
- Service name tagging
- Request logging utilities

**Usage:**
```python
from shared.logging import setup_logging, log_event

logger = setup_logging("my-service", level="INFO")
logger.info("Service started")

log_event(logger, "user_created", {"user_id": 123}, "correlation-123")
```

### Utilities (`utils.py`)

Common utility functions:
- UUID generation
- File handling
- Validation functions
- Circuit breaker implementation
- String manipulation

**Usage:**
```python
from shared.utils import generate_uuid, sanitize_filename, CircuitBreaker

id = generate_uuid()
safe_name = sanitize_filename("my file.pdf")

breaker = CircuitBreaker()
result = breaker.call(some_function, arg1, arg2)
```

## Service Generation

Use the service generator to create new microservices:

```bash
cd microservices/shared
python generate_service.py user-service 8005 --title "User Service" --description "User management service"
```

This creates a complete service structure with:
- FastAPI application
- Docker configuration
- Environment variables
- Directory structure
- README documentation

## Docker Base Image

Build the base image for all services:

```bash
cd microservices
docker build -f shared/Dockerfile.base -t microservices/shared:base .
```

Services can then extend this base image:

```dockerfile
FROM microservices/shared:base
# Service-specific configuration
```

## Development Setup

1. Install shared dependencies:
   ```bash
   pip install -r shared/requirements.txt
   ```

2. Set up environment variables (each service needs its own `.env` file)

3. Use the shared libraries in your service:
   ```python
   from shared.base_app import create_service
   from shared.config import get_config
   from shared.database import get_db_dependency
   ```

## Best Practices

1. **Configuration**: Use environment variables for all configuration
2. **Logging**: Always include correlation IDs in logs
3. **Error Handling**: Use custom exceptions with proper error codes
4. **Database**: Use the repository pattern for data access
5. **Inter-service Communication**: Use the HTTP client with circuit breakers
6. **Events**: Publish domain events for important state changes
7. **Health Checks**: Implement proper health check endpoints

## Testing

The shared libraries include testing utilities. Each service should have:
- Unit tests for business logic
- Integration tests for database operations
- Contract tests for API endpoints

## Security

- Use JWT tokens for authentication
- Validate all inputs
- Use HTTPS in production
- Implement rate limiting
- Log security events

## Monitoring

- Use structured logging
- Implement health checks
- Monitor circuit breaker states
- Track response times
- Set up alerts for errors