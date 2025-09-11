# Documentación de Endpoints - Aurora Microservices

## Resumen General

La aplicación Aurora está construida con una arquitectura de microservicios usando FastAPI. Cada servicio expone endpoints REST y cuenta con documentación automática de Swagger disponible en `/docs`.

## Servicios Disponibles

### 1. Config Service (Puerto 8004)
**URL Base:** `http://localhost:8004`
**Descripción:** Servicio centralizado para gestión de configuraciones y feature flags

#### Endpoints Principales

##### Root Endpoints
- `GET /` - Información del servicio y endpoints disponibles
- `GET /status` - Estado del servicio y características
- `GET /health` - Health check básico
- `GET /health/ready` - Readiness check con dependencias
- `GET /health/live` - Liveness check
- `GET /health/detailed` - Health check detallado

##### Configuraciones (`/api/v1/configurations`)
- `POST /api/v1/configurations/` - Crear nueva configuración
- `GET /api/v1/configurations/` - Listar configuraciones con filtros
  - Query params: `environment`, `service_name`, `is_active`, `include_sensitive`, `skip`, `limit`
- `GET /api/v1/configurations/bulk` - Obtener configuraciones como pares clave-valor
- `GET /api/v1/configurations/{config_id}` - Obtener configuración por ID
- `GET /api/v1/configurations/key/{config_key}` - Obtener configuración por clave
- `GET /api/v1/configurations/value/{config_key}` - Obtener valor de configuración directamente
- `PUT /api/v1/configurations/{config_id}` - Actualizar configuración por ID
- `PUT /api/v1/configurations/key/{config_key}` - Establecer valor de configuración
- `DELETE /api/v1/configurations/{config_id}` - Eliminar configuración
- `GET /api/v1/configurations/{config_id}/history` - Historial de cambios

##### Feature Flags (`/api/v1/feature-flags`)
- `POST /api/v1/feature-flags/` - Crear nuevo feature flag
- `GET /api/v1/feature-flags/` - Listar feature flags con filtros
  - Query params: `environment`, `service_name`, `is_enabled`, `include_expired`, `skip`, `limit`
- `GET /api/v1/feature-flags/bulk` - Obtener feature flags como pares clave-valor
- `GET /api/v1/feature-flags/{flag_id}` - Obtener feature flag por ID
- `GET /api/v1/feature-flags/key/{flag_key}` - Obtener feature flag por clave
- `GET /api/v1/feature-flags/evaluate/{flag_key}` - Evaluar feature flag para usuario
- `GET /api/v1/feature-flags/check/{flag_key}` - Verificación booleana simple
- `PUT /api/v1/feature-flags/{flag_id}` - Actualizar feature flag
- `PUT /api/v1/feature-flags/toggle/{flag_key}` - Activar/desactivar feature flag
- `PUT /api/v1/feature-flags/rollout/{flag_key}` - Actualizar porcentaje de rollout
- `DELETE /api/v1/feature-flags/{flag_id}` - Eliminar feature flag

##### Service Discovery (`/api/v1/discovery`)
- `GET /api/v1/discovery/services` - Obtener todos los servicios registrados
- `GET /api/v1/discovery/services/healthy` - Obtener servicios saludables
- `GET /api/v1/discovery/services/{service_name}` - Información de servicio específico
- `POST /api/v1/discovery/services/{service_name}/heartbeat` - Enviar heartbeat
- `DELETE /api/v1/discovery/services/{service_name}` - Desregistrar servicio
- `POST /api/v1/discovery/cleanup` - Limpiar servicios obsoletos
- `GET /api/v1/discovery/health-check/{service_name}` - Health check de servicio
- `GET /api/v1/discovery/health-check-all` - Health check de todos los servicios

### 2. Demo Service (Puerto 9998)
**URL Base:** `http://localhost:9998`
**Descripción:** Servicio de demostración para testing

#### Endpoints
- `GET /` - Root endpoint
- `GET /health` - Health check básico
- `GET /health/ready` - Readiness check
- `GET /health/live` - Liveness check
- `GET /health/detailed` - Health check detallado

##### Items API (`/api/v1`)
- `GET /api/v1/items/` - Listar items con paginación
  - Query params: `skip`, `limit`
- `GET /api/v1/items/{item_id}` - Obtener item por ID
- `POST /api/v1/items/` - Crear nuevo item
- `PUT /api/v1/items/{item_id}` - Actualizar item
- `DELETE /api/v1/items/{item_id}` - Eliminar item

### 3. Sample API Service (Puerto 8888)
**URL Base:** `http://localhost:8888`
**Descripción:** API de ejemplo generada para demostración

#### Endpoints
- `GET /` - Root endpoint
- `GET /health` - Health check básico
- `GET /health/ready` - Readiness check
- `GET /health/live` - Liveness check
- `GET /health/detailed` - Health check detallado

##### Items API (`/api/v1`)
- `GET /api/v1/items/` - Listar items con paginación
- `GET /api/v1/items/{item_id}` - Obtener item por ID
- `POST /api/v1/items/` - Crear nuevo item
- `PUT /api/v1/items/{item_id}` - Actualizar item
- `DELETE /api/v1/items/{item_id}` - Eliminar item

### 4. Test Generated Service (Puerto por defecto)
**Descripción:** Servicio de prueba generado

#### Endpoints
- `GET /` - Root endpoint
- `GET /health` - Health check básico
- `GET /health/ready` - Readiness check
- `GET /health/live` - Liveness check
- `GET /health/detailed` - Health check detallado

##### Items API (`/api/v1`)
- `GET /api/v1/items/` - Listar items con paginación
- `GET /api/v1/items/{item_id}` - Obtener item por ID
- `POST /api/v1/items/` - Crear nuevo item
- `PUT /api/v1/items/{item_id}` - Actualizar item
- `DELETE /api/v1/items/{item_id}` - Eliminar item

### 5. Test Service (Puerto por defecto)
**Descripción:** Servicio para testing de librerías compartidas

#### Endpoints
- `GET /` - Root endpoint
- `GET /health` - Health check básico
- `GET /health/ready` - Readiness check
- `GET /health/live` - Liveness check
- `GET /health/detailed` - Health check detallado

##### Items API (`/api/v1`)
- `GET /api/v1/items/` - Listar items con paginación
- `GET /api/v1/items/{item_id}` - Obtener item por ID
- `POST /api/v1/items/` - Crear nuevo item
- `PUT /api/v1/items/{item_id}` - Actualizar item
- `DELETE /api/v1/items/{item_id}` - Eliminar item

## Servicios Configurados (Sin implementación activa)

### API Gateway (Puerto 8000)
**URL Base:** `http://localhost:8000`
**Estado:** Configurado pero sin implementación activa

### Subject Service (Puerto 8002)
**URL Base:** `http://localhost:8002`
**Estado:** Configurado pero sin implementación activa

### Syllabus Service (Puerto 8001)
**URL Base:** `http://localhost:8001`
**Estado:** Configurado pero sin implementación activa

### File Service (Puerto 8003)
**URL Base:** `http://localhost:8003`
**Estado:** Configurado pero sin implementación activa

## Características Comunes

### Health Checks
Todos los servicios implementan los siguientes endpoints de salud:
- `/health` - Health check básico
- `/health/ready` - Readiness check (incluye dependencias)
- `/health/live` - Liveness check
- `/health/detailed` - Health check detallado con todos los componentes

### Documentación Automática
Cada servicio expone documentación Swagger en:
- `/docs` - Interfaz Swagger UI
- `/redoc` - Documentación ReDoc alternativa
- `/openapi.json` - Especificación OpenAPI

### Middleware Común
- **CORS:** Configurado para permitir orígenes múltiples
- **Logging:** Logging estructurado con correlation IDs
- **Error Handling:** Manejo centralizado de errores
- **Request Tracking:** Seguimiento de requests con correlation IDs

### Autenticación y Seguridad
- JWT tokens configurados (pendiente implementación completa)
- Rate limiting configurado
- Trusted host middleware en producción

## Base de Datos

### TiDB Cluster
La aplicación utiliza un cluster TiDB con los siguientes componentes:
- **TiDB SQL Layer:** Puerto 4000
- **PD (Placement Driver):** Puerto 2379
- **TiKV Storage Nodes:** Puertos 20160, 20161, 20162
- **TiDB Dashboard:** Puerto 12333

### Configuración de Base de Datos
Cada servicio tiene su propia base de datos:
- `config_service_db` - Config Service
- `demo_service_db` - Demo Service
- `sample_api_db` - Sample API Service

## Service Discovery

El sistema incluye service discovery automático que permite:
- Registro automático de servicios
- Health checks distribuidos
- Descubrimiento de servicios entre microservicios
- Cleanup automático de servicios obsoletos

## Ejemplos de Uso

### Obtener todas las configuraciones
```bash
curl -X GET "http://localhost:8004/api/v1/configurations/" \
  -H "accept: application/json"
```

### Crear un feature flag
```bash
curl -X POST "http://localhost:8004/api/v1/feature-flags/" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "flag_key": "new_feature",
    "description": "Nueva característica",
    "is_enabled": true,
    "environment": "development"
  }'
```

### Health check de un servicio
```bash
curl -X GET "http://localhost:8004/health/ready" \
  -H "accept: application/json"
```

## Notas Importantes

1. **Desarrollo Activo:** Solo el Config Service tiene implementación completa
2. **Puertos:** Verificar archivos `.env` para puertos específicos de cada servicio
3. **Documentación:** Usar `/docs` en cada servicio para documentación interactiva
4. **Logs:** Todos los servicios generan logs estructurados con correlation IDs
5. **Base de Datos:** Asegurar que TiDB esté ejecutándose antes de iniciar servicios

## Próximos Pasos

Para servicios sin implementación completa:
1. Implementar lógica de negocio específica
2. Definir esquemas de datos
3. Crear repositorios y servicios
4. Implementar endpoints específicos del dominio
5. Agregar tests de integración