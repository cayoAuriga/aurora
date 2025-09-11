# Configuration Service

A centralized configuration and feature flags management service built with FastAPI and TiDB.

## 🏗️ Refactored Architecture

This service has been refactored into a clean, modular structure based on the working `main.py` implementation. The new architecture separates concerns and makes the codebase more maintainable.

### 📁 Project Structure

```
config-service/
├── main.py              # Main application entry point (refactored)
├── app.py               # Alternative entry point for deployment
├── config.py            # Configuration management (no hardcoded values)
├── models.py            # Pydantic models
├── database.py          # Database connection and initialization
├── routers.py           # API routers and endpoints
├── test_service.py      # Service verification tests
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── README.md           # This file
└── tests/              # Test files
```

## ✨ Features

- **Configuration Management**: Store and retrieve application configurations
- **Feature Flags**: Manage feature toggles with rollout percentages
- **Environment Support**: Different configurations per environment
- **Service-specific Configs**: Configurations scoped to specific services
- **TiDB Integration**: Cloud-native distributed SQL database
- **Real-time Updates**: Live configuration changes
- **RESTful API**: Complete CRUD operations
- **OpenAPI Documentation**: Auto-generated API docs
- **Modular Architecture**: Clean separation of concerns
- **No Hardcoded Values**: All configuration via environment variables

## 🚀 Quick Start

1. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**:

   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

3. **Test the Refactored Service**:

   ```bash
   python test_service.py
   ```

4. **Run the Service**:

   ```bash
   # Option 1: Direct main.py
   python main.py

   # Option 2: Using app.py
   python app.py

   # Option 3: Using uvicorn
   uvicorn main:app --host 0.0.0.0 --port 8004 --reload
   ```

5. **Access API Documentation**:
   - Swagger UI: http://localhost:8004/docs
   - ReDoc: http://localhost:8004/redoc

## 🔧 Configuration

All configuration is handled through environment variables (no hardcoded values):

| Variable       | Description             | Default          |
| -------------- | ----------------------- | ---------------- |
| `SERVICE_NAME` | Service identifier      | `config-service` |
| `SERVICE_PORT` | Port to run the service | `8004`           |
| `ENVIRONMENT`  | Environment name        | `development`    |
| `DEBUG`        | Enable debug mode       | `false`          |
| `LOG_LEVEL`    | Logging level           | `INFO`           |
| `HOST`         | Service host            | `127.0.0.1`      |
| `DB_HOST`      | Database host           | TiDB Cloud host  |
| `DB_PORT`      | Database port           | `4000`           |
| `DB_USERNAME`  | Database username       | -                |
| `DB_PASSWORD`  | Database password       | -                |
| `DB_DATABASE`  | Database name           | `config_db`      |
| `DB_SSL_CA`    | SSL certificate path    | -                |

## 📡 API Endpoints

### Configuration Management

- `POST /api/v1/configurations/` - Create configuration
- `GET /api/v1/configurations/` - List all configurations
- `GET /api/v1/configurations/key/{key}` - Get configuration by key

### Feature Flags

- `POST /api/v1/feature-flags/` - Create feature flag
- `GET /api/v1/feature-flags/` - List all feature flags
- `GET /api/v1/feature-flags/check/{key}` - Check if flag is enabled

### Service Information

- `GET /` - Service information
- `GET /status` - Service status and health

## 🗄️ Database Schema

### app_configurations

- `id` - Primary key
- `config_key` - Configuration key
- `config_value` - Configuration value
- `environment` - Environment (development, staging, production)
- `service_name` - Service name (global for shared configs)
- `description` - Optional description
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

### feature_flags

- `id` - Primary key
- `flag_name` - Human-readable flag name
- `flag_key` - Unique flag identifier
- `description` - Optional description
- `is_enabled` - Flag status (true/false)
- `rollout_percentage` - Percentage of users to enable (0-100)
- `environment` - Environment scope
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

## 🧪 Testing

Run the verification tests to ensure everything works:

```bash
python test_service.py
```

This will test:

- Module imports
- Configuration loading
- App creation
- Route registration

## 🔄 Refactoring Changes

### What was removed:

- Old modular directories (`models/`, `routers/`, `services/`, `repositories/`, `schemas/`, `database/`)
- Unused files (`app.py`, `main_simple.py`, `diagnose.py`)
- Hardcoded configuration values

### What was added:

- `config.py` - Centralized configuration management
- `models.py` - Clean Pydantic models
- `database.py` - Database connection and initialization
- `routers.py` - API endpoints and routing
- `test_service.py` - Service verification
- Environment-based configuration

### What was improved:

- Modular architecture with clear separation of concerns
- No hardcoded values (everything configurable via environment)
- Cleaner imports and dependencies
- Better error handling and logging
- Simplified deployment options

## 🚀 Deployment

### Option 1: Direct Python

```bash
python main.py
```

### Option 2: Using uvicorn

```bash
uvicorn main:app --host 0.0.0.0 --port 8004
```

### Option 3: Using app.py

```bash
uvicorn app:app --host 0.0.0.0 --port 8004
```

### Option 4: Docker

```bash
docker build -t config-service .
docker run -p 8004:8004 config-service
```

## 🔍 Usage Examples

### Configuration Management

```python
import httpx

# Create a configuration
config_data = {
    "config_key": "api_timeout",
    "config_value": "30",
    "environment": "production",
    "service_name": "user-service",
    "description": "API timeout in seconds"
}

response = httpx.post("http://localhost:8004/api/v1/configurations/", json=config_data)
print(response.json())

# Get configuration by key
response = httpx.get(
    "http://localhost:8004/api/v1/configurations/key/api_timeout",
    params={"environment": "production", "service_name": "user-service"}
)
print(response.json())
```

### Feature Flags

```python
import httpx

# Create a feature flag
flag_data = {
    "flag_name": "New Dashboard",
    "flag_key": "new_dashboard",
    "description": "Enable new dashboard UI",
    "is_enabled": True,
    "rollout_percentage": 50,
    "environment": "production"
}

response = httpx.post("http://localhost:8004/api/v1/feature-flags/", json=flag_data)
print(response.json())

# Check if flag is enabled
response = httpx.get(
    "http://localhost:8004/api/v1/feature-flags/check/new_dashboard",
    params={"user_id": "user123", "environment": "production"}
)
print(response.json())  # {"enabled": true/false}
```

## 🔧 Development

### Adding New Features

1. Add models to `models.py`
2. Add database operations to `database.py`
3. Add API endpoints to `routers.py`
4. Update configuration in `config.py` if needed
5. Test with `test_service.py`

### Running in Development

```bash
# With auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8004
```

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors**

   - Run `python test_service.py` to verify all modules load correctly
   - Check that shared libraries are accessible

2. **Database Connection Errors**

   - Verify environment variables in `.env`
   - Check TiDB Cloud connectivity
   - Verify SSL certificate path

3. **Configuration Issues**
   - All values are now environment-based
   - Check `.env` file for missing variables
   - Use defaults defined in `config.py`

### Verification Steps

```bash
# 1. Test imports and configuration
python test_service.py

# 2. Check service status
curl http://localhost:8004/status

# 3. Check API documentation
open http://localhost:8004/docs
```

## 📋 For Postman Testing

See the `POSTMAN_TESTING.md` file for detailed instructions on how to test all endpoints with Postman.

## 🔗 Integration with Other Services

The Configuration Service is designed to be consumed by other microservices in the Aurora ecosystem:

```python
# Example: Using configurations in another service
import httpx

async def get_config(key: str, service_name: str = "global"):
    response = await httpx.AsyncClient().get(
        f"http://config-service:8004/api/v1/configurations/key/{key}",
        params={"service_name": service_name}
    )
    if response.status_code == 200:
        return response.json()["config_value"]
    return None

# Example: Checking feature flags
async def is_feature_enabled(flag_key: str, user_id: str = None):
    response = await httpx.AsyncClient().get(
        f"http://config-service:8004/api/v1/feature-flags/check/{flag_key}",
        params={"user_id": user_id} if user_id else {}
    )
    if response.status_code == 200:
        return response.json()["enabled"]
    return False
```
# routers.py (versión funcional)
from functools import partial
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Callable

from database import get_db
from dependencies import get_configuration_functions, get_configuration_repository, get_enhanced_configuration_functions, get_update_configuration_fn
from models.schemas import ConfigurationCreate, ConfigurationUpdate, ConfigurationResponse

config_router = APIRouter()

# === OPCIÓN 1: USANDO DICCIONARIO DE FUNCIONES ===

@config_router.post("/configurations/", response_model=ConfigurationResponse)
async def create_configuration(
    config_data: ConfigurationCreate,
    db: Session = Depends(get_db),
    service_fns: Dict[str, Callable] = Depends(get_configuration_functions)
    #                                    ↑
    #                    Inyectamos un dict de funciones en lugar de una clase
):
    """
    Crear configuración usando servicios funcionales
    
    ¿Cómo funciona la inyección aquí?
    1. get_configuration_functions() retorna un dict de funciones
    2. Cada función ya tiene el repository "baked in" via partial()
    3. Solo necesitamos pasar db y los parámetros específicos
    """
    return service_fns['create'](db, config_data)

@config_router.get("/configurations/", response_model=List[ConfigurationResponse])
async def list_configurations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    service_fns: Dict[str, Callable] = Depends(get_configuration_functions)
):
    """Listar configuraciones"""
    return service_fns['get_all'](db, skip, limit)

@config_router.get("/configurations/{config_id}", response_model=ConfigurationResponse)
async def get_configuration(
    config_id: int,
    db: Session = Depends(get_db),
    service_fns: Dict[str, Callable] = Depends(get_configuration_functions)
):
    """Obtener configuración por ID"""
    return service_fns['get_by_id'](db, config_id)

@config_router.get("/configurations/key/{config_key}", response_model=ConfigurationResponse)
async def get_configuration_by_key(
    config_key: str,
    environment: str = Query("development"),
    service_name: str = Query("global"),
    db: Session = Depends(get_db),
    service_fns: Dict[str, Callable] = Depends(get_configuration_functions)
):
    """Obtener configuración por clave"""
    return service_fns['get_by_key'](db, config_key, environment, service_name)

# === OPCIÓN 2: INYECCIÓN DE FUNCIONES INDIVIDUALES ===

@config_router.put("/configurations/{config_id}", response_model=ConfigurationResponse)
async def update_configuration(
    config_id: int,
    config_data: ConfigurationUpdate,
    db: Session = Depends(get_db),
    update_fn: Callable = Depends(get_update_configuration_fn),
):
    return update_fn(db, config_id, config_data)

# === OPCIÓN 3: USANDO ENHANCED FUNCTIONS ===

@config_router.delete("/configurations/{config_id}")
async def delete_configuration(
    config_id: int,
    db: Session = Depends(get_db),
    service_fns: Dict[str, Callable] = Depends(get_enhanced_configuration_functions)
    #                                           ↑
    #                        Estas funciones ya tienen logging y error handling
):
    """Eliminar configuración con enhanced functions"""
    service_fns['delete'](db, config_id)
    return {"message": f"Configuration {config_id} deleted successfully"}