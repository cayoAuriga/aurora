# Configuration Service

Centralized configuration and feature flags management service for Aurora microservices architecture.

## Features

- **Configuration Management**: Store and manage application configurations
- **Feature Flags**: Control feature rollouts with percentage-based gradual deployment
- **Environment Support**: Different configurations for development, staging, and production
- **Service-specific Configs**: Configurations scoped to specific microservices
- **Configuration History**: Track all configuration changes with audit logs
- **RESTful API**: Complete CRUD operations via REST endpoints

## Architecture

The Configuration Service follows the CQRS pattern and includes:

- **Models**: SQLAlchemy models for database entities
- **Schemas**: Pydantic schemas for request/response validation
- **Repositories**: Data access layer with business logic
- **Services**: Business logic layer
- **Routers**: FastAPI route handlers

## Setup

1. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

2. Install dependencies:
   ```bash
   pip install -r ../shared/requirements.txt
   pip install -r requirements.txt
   ```

3. Set up the database (TiDB):
   ```bash
   # Run the database schema
   mysql -h localhost -P 4000 -u root < database/schema.sql
   ```

4. Run the service:
   ```bash
   python main.py
   ```

## API Endpoints

### Configuration Management

- `POST /api/v1/configurations/` - Create configuration
- `GET /api/v1/configurations/` - List configurations
- `GET /api/v1/configurations/{id}` - Get configuration by ID
- `GET /api/v1/configurations/key/{key}` - Get configuration by key
- `GET /api/v1/configurations/value/{key}` - Get configuration value directly
- `PUT /api/v1/configurations/{id}` - Update configuration
- `PUT /api/v1/configurations/key/{key}` - Set configuration value
- `DELETE /api/v1/configurations/{id}` - Delete configuration
- `GET /api/v1/configurations/{id}/history` - Get configuration history
- `GET /api/v1/configurations/bulk` - Get configurations as key-value pairs

### Feature Flags

- `POST /api/v1/feature-flags/` - Create feature flag
- `GET /api/v1/feature-flags/` - List feature flags
- `GET /api/v1/feature-flags/{id}` - Get feature flag by ID
- `GET /api/v1/feature-flags/key/{key}` - Get feature flag by key
- `GET /api/v1/feature-flags/evaluate/{key}` - Evaluate feature flag
- `GET /api/v1/feature-flags/check/{key}` - Simple boolean check
- `PUT /api/v1/feature-flags/{id}` - Update feature flag
- `PUT /api/v1/feature-flags/toggle/{key}` - Toggle feature flag
- `PUT /api/v1/feature-flags/rollout/{key}` - Update rollout percentage
- `DELETE /api/v1/feature-flags/{id}` - Delete feature flag
- `GET /api/v1/feature-flags/bulk` - Get feature flags as key-value pairs

## Usage Examples

### Configuration Management

```python
# Create a configuration
POST /api/v1/configurations/
{
    "config_key": "database.max_connections",
    "config_value": 100,
    "environment": "production",
    "service_name": "user-service",
    "description": "Maximum database connections"
}

# Get configuration value
GET /api/v1/configurations/value/database.max_connections?environment=production&service_name=user-service
```

### Feature Flags

```python
# Create a feature flag
POST /api/v1/feature-flags/
{
    "flag_name": "New Dashboard",
    "flag_key": "new_dashboard",
    "description": "Enable new dashboard UI",
    "is_enabled": true,
    "rollout_percentage": 25,
    "environment": "production"
}

# Check if feature is enabled for user
GET /api/v1/feature-flags/check/new_dashboard?user_id=123

# Gradually increase rollout
PUT /api/v1/feature-flags/rollout/new_dashboard?percentage=50
```

## Testing

Run the validation tests:
```bash
python simple_test.py
```

Run unit tests:
```bash
pytest tests/
```

## Docker

Build and run with Docker:

```bash
docker build -t aurora-config-service .
docker run -p 8004:8004 aurora-config-service
```

Or use Docker Compose:

```bash
docker-compose up
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8004/docs
- ReDoc: http://localhost:8004/redoc
- Service Status: http://localhost:8004/status

## Health Checks

- Basic health: http://localhost:8004/health
- Readiness: http://localhost:8004/health/ready
- Liveness: http://localhost:8004/health/live

## Database Schema

The service uses the following main tables:

- `app_configurations` - Application configurations
- `config_history` - Configuration change history
- `feature_flags` - Feature flag definitions

See `database/schema.sql` for the complete schema.
