# Microservices Optimization Design Document

## Overview

This design transforms the existing monolithic Aurora FastAPI application into a microservices architecture. The current application follows CQRS pattern with a single syllabus management domain. The microservices architecture will decompose this into independent services while maintaining the existing CQRS benefits and adding scalability, resilience, and independent deployment capabilities.

### Current Architecture Analysis
- **Monolithic FastAPI application** with single database (TiDB Cloud)
- **CQRS pattern** already implemented (commands/queries separation)
- **Repository pattern** for data access abstraction
- **Single domain**: Syllabus management with subject relationships
- **Database**: MySQL-compatible TiDB Cloud with SSL

### Target Architecture
- **API Gateway**: Single entry point for all client requests
- **Syllabus Service**: Core domain service for syllabus management
- **Subject Service**: Extracted service for subject management (inferred from foreign key)
- **File Service**: Dedicated service for file URL management and storage
- **Configuration Service**: Centralized configuration management
- **Service Discovery**: Automatic service registration and discovery
- **Message Broker**: Asynchronous communication between services

## Architecture

### Service Decomposition Strategy

#### 1. API Gateway Service
- **Purpose**: Single entry point, routing, cross-cutting concerns
- **Technology**: FastAPI with reverse proxy capabilities
- **Responsibilities**:
  - Request routing to appropriate microservices
  - Authentication and authorization
  - Rate limiting and throttling
  - Request/response transformation
  - Circuit breaker implementation
  - API versioning management

#### 2. Syllabus Service
- **Purpose**: Core syllabus domain logic
- **Technology**: FastAPI with dedicated database
- **Responsibilities**:
  - Syllabus CRUD operations
  - Business logic validation
  - Event publishing for syllabus changes
  - Integration with Subject and File services

#### 3. Subject Service
- **Purpose**: Subject management and metadata
- **Technology**: FastAPI with dedicated database
- **Responsibilities**:
  - Subject CRUD operations
  - Subject validation and business rules
  - Subject-related queries and reporting
  - Event publishing for subject changes

#### 4. File Service
- **Purpose**: File storage and URL management
- **Technology**: FastAPI with object storage integration
- **Responsibilities**:
  - File upload and storage
  - File URL generation and validation
  - File metadata management
  - Integration with cloud storage providers

#### 5. Configuration Service
- **Purpose**: Centralized configuration management
- **Technology**: FastAPI with configuration store
- **Responsibilities**:
  - Service configuration management
  - Environment-specific settings
  - Feature flags and toggles
  - Configuration versioning

### Communication Patterns

#### Synchronous Communication
- **REST APIs**: For real-time queries and commands
- **Service-to-Service**: Direct HTTP calls for immediate consistency needs
- **API Gateway Routing**: Client requests routed through gateway

#### Asynchronous Communication
- **Event-Driven**: Domain events for eventual consistency
- **Message Queues**: Redis/RabbitMQ for reliable message delivery
- **Event Sourcing**: Optional for audit trails and replay capabilities

### Data Architecture

#### Database Per Service Pattern
- **Syllabus DB**: Dedicated database for syllabus data
- **Subject DB**: Dedicated database for subject data
- **File DB**: Metadata storage for file information
- **Config DB**: Configuration and settings storage

#### Data Consistency Strategy
- **Strong Consistency**: Within service boundaries
- **Eventual Consistency**: Across service boundaries via events
- **Saga Pattern**: For distributed transactions
- **Compensation Actions**: For rollback scenarios

## Components and Interfaces

### API Gateway Interface
```python
# Gateway routing configuration
routes = {
    "/api/v1/syllabus/*": "syllabus-service:8001",
    "/api/v1/subjects/*": "subject-service:8002", 
    "/api/v1/files/*": "file-service:8003",
    "/api/v1/config/*": "config-service:8004"
}
```

### Service Interfaces

#### Syllabus Service API
```python
# REST Endpoints
POST /syllabus/                    # Create syllabus
GET /syllabus/{subject_id}         # Get syllabus by subject
PUT /syllabus/{syllabus_id}        # Update syllabus
DELETE /syllabus/{syllabus_id}     # Delete syllabus

# Events Published
SyllabusCreated, SyllabusUpdated, SyllabusDeleted
```

#### Subject Service API
```python
# REST Endpoints  
POST /subjects/                    # Create subject
GET /subjects/{subject_id}         # Get subject
GET /subjects/                     # List subjects
PUT /subjects/{subject_id}         # Update subject
DELETE /subjects/{subject_id}      # Delete subject

# Events Published
SubjectCreated, SubjectUpdated, SubjectDeleted
```

#### File Service API
```python
# REST Endpoints
POST /files/upload                 # Upload file
GET /files/{file_id}              # Get file metadata
DELETE /files/{file_id}           # Delete file
GET /files/{file_id}/url          # Get download URL

# Events Published
FileUploaded, FileDeleted
```

### Inter-Service Communication

#### Service Discovery
- **Technology**: Consul or etcd for service registry
- **Health Checks**: Regular health check endpoints
- **Load Balancing**: Client-side or server-side load balancing

#### Event Schema
```python
class DomainEvent:
    event_id: str
    event_type: str
    aggregate_id: str
    aggregate_type: str
    event_data: dict
    timestamp: datetime
    correlation_id: str
```

## Data Models

### Syllabus Service Models
```python
class Syllabus:
    id: int
    subject_id: int  # Reference to Subject Service
    file_id: str     # Reference to File Service
    created_at: datetime
    updated_at: datetime
    version: int
```

### Subject Service Models
```python
class Subject:
    id: int
    name: str
    code: str
    description: str
    department_id: int
    credits: int
    created_at: datetime
    updated_at: datetime
```

### File Service Models
```python
class FileMetadata:
    id: str
    original_name: str
    file_type: str
    file_size: int
    storage_path: str
    public_url: str
    created_at: datetime
    expires_at: datetime
```

### Event Store Models
```python
class EventStore:
    event_id: str
    stream_id: str
    event_type: str
    event_data: json
    metadata: json
    timestamp: datetime
    version: int
```

## Error Handling

### Circuit Breaker Pattern
- **Implementation**: Hystrix-like circuit breaker for service calls
- **Fallback Mechanisms**: Cached responses or default values
- **Timeout Configuration**: Service-specific timeout settings
- **Retry Logic**: Exponential backoff with jitter

### Error Response Standards
```python
class ErrorResponse:
    error_code: str
    error_message: str
    correlation_id: str
    timestamp: datetime
    service_name: str
    details: dict
```

### Distributed Tracing
- **Technology**: Jaeger or Zipkin for request tracing
- **Correlation IDs**: Unique identifiers for request tracking
- **Span Creation**: Service boundary and operation tracking

## Testing Strategy

### Unit Testing
- **Service Level**: Individual service unit tests
- **Repository Level**: Data access layer testing
- **Command/Query Level**: CQRS component testing

### Integration Testing
- **Service Integration**: API contract testing
- **Database Integration**: Repository integration tests
- **Message Queue Integration**: Event publishing/consuming tests

### Contract Testing
- **Consumer-Driven Contracts**: Pact or similar framework
- **API Schema Validation**: OpenAPI specification testing
- **Event Schema Testing**: Event contract validation

### End-to-End Testing
- **User Journey Testing**: Critical path automation
- **Cross-Service Testing**: Multi-service workflow validation
- **Performance Testing**: Load and stress testing

### Testing Infrastructure
```python
# Test containers for integration testing
test_containers = {
    "database": "mysql:8.0",
    "redis": "redis:7.0",
    "message_broker": "rabbitmq:3.11"
}
```

## Deployment and Infrastructure

### Containerization
- **Docker**: Each service containerized independently
- **Multi-stage Builds**: Optimized container images
- **Base Images**: Standardized Python base images
- **Security Scanning**: Container vulnerability scanning

### Orchestration
- **Docker Compose**: Development environment
- **Kubernetes**: Production orchestration (optional)
- **Service Mesh**: Istio for advanced traffic management (optional)

### Configuration Management
- **Environment Variables**: Service-specific configuration
- **Config Maps**: Kubernetes configuration management
- **Secrets Management**: Secure credential storage
- **Feature Flags**: Runtime configuration changes

### Monitoring and Observability
- **Metrics**: Prometheus for metrics collection
- **Logging**: Centralized logging with ELK stack
- **Health Checks**: Service health monitoring
- **Alerting**: Alert manager for critical issues

## Migration Strategy

### Phase 1: Infrastructure Setup
- Set up service discovery and configuration management
- Implement API Gateway with routing to monolith
- Set up monitoring and logging infrastructure

### Phase 2: Service Extraction
- Extract Subject Service from monolith
- Extract File Service from monolith
- Implement event-driven communication

### Phase 3: Core Service Migration
- Migrate Syllabus Service with new architecture
- Implement cross-service communication
- Update API Gateway routing

### Phase 4: Optimization
- Implement caching strategies
- Optimize database queries and connections
- Fine-tune performance and monitoring