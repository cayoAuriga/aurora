# Aurora Microservices Architecture

This directory contains the microservices implementation of the Aurora application, decomposed from the original monolithic structure.

## Architecture Overview

The system is composed of the following services:

- **API Gateway** (Port 8000): Entry point for all client requests, handles routing, authentication, and cross-cutting concerns
- **Syllabus Service** (Port 8001): Core syllabus domain logic with CQRS pattern
- **Subject Service** (Port 8002): Subject management and metadata
- **File Service** (Port 8003): File storage and URL management
- **Configuration Service** (Port 8004): Centralized configuration management

## Shared Components

The `shared/` directory contains common utilities used across all services:

- **Logging**: Structured logging with correlation ID support
- **Error Handling**: Standardized error responses and exception handling
- **Event Schemas**: Domain event definitions for inter-service communication
- **Base App**: FastAPI application template with common middleware

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Running with Docker Compose

1. Build and start all services:
```bash
cd microservices
docker-compose up --build
```

2. Services will be available at:
- API Gateway: http://localhost:8000
- Syllabus Service: http://localhost:8001
- Subject Service: http://localhost:8002
- File Service: http://localhost:8003
- Configuration Service: http://localhost:8004

### Running Individual Services Locally

1. Install dependencies:
```bash
pip install -r shared/requirements.txt
```

2. Set environment variables:
```bash
export PYTHONPATH=/path/to/microservices
export DATABASE_URL=mysql+pymysql://user:password@localhost:3306/database_name
```

3. Run a service:
```bash
cd api-gateway
python main.py
```

## Health Checks

Each service exposes health check endpoints:

- `/health` - Basic health status
- `/health/ready` - Readiness check including dependencies

## Development

### Adding New Routes

1. Create route modules in the service directory
2. Import and add routes to the main application in `main.py`
3. Follow the CQRS pattern for commands and queries

### Event Publishing

Use the shared event schemas and publisher interface:

```python
from shared import DomainEvent, EventPublisher

# Create and publish events
event = SyllabusCreatedEvent(
    aggregate_id="123",
    event_data={"name": "New Syllabus"},
    correlation_id=correlation_id
)
await event_publisher.publish(event)
```

### Error Handling

Use shared exception classes:

```python
from shared import NotFoundError, ValidationException

# Raise service-specific errors
raise NotFoundError("Syllabus", syllabus_id, "syllabus-service")
```

## Testing

Run tests for individual services:

```bash
cd syllabus-service
pytest
```

## Configuration

Services use environment variables for configuration:

- `PORT`: Service port number
- `SERVICE_NAME`: Service identifier
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection string (default: redis://localhost:6379)

## Next Steps

This is the basic project structure. The following tasks will implement:

1. Service discovery and configuration infrastructure
2. Individual service implementations with CQRS
3. Inter-service communication
4. Event-driven architecture
5. Monitoring and observability