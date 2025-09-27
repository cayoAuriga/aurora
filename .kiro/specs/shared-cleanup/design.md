# Design Document

## Overview

Este diseño describe cómo limpiar el directorio `./microservices/shared` eliminando archivos obsoletos y manteniendo solo los componentes que realmente utiliza el `config-service`. El objetivo es tener un directorio shared minimalista y funcional que soporte la arquitectura actual.

## Architecture

### Current State Analysis

Después de revisar ambos directorios, se identificaron las siguientes categorías de archivos:

1. **Archivos Core Utilizados**: Archivos que son importados por config-service
2. **Archivos Obsoletos**: Funcionalidades no utilizadas en la arquitectura actual
3. **Archivos de Prueba/Demo**: Scripts de testing y demostración innecesarios
4. **Archivos de Cache/Build**: Archivos temporales generados automáticamente
5. **Templates y Generadores**: Herramientas de generación que no se usan

### Target State

El directorio shared limpio contendrá solo:
- Archivos de logging que usa config-service (`aurora_logging.py`)
- Archivos de configuración base si son necesarios
- Archivos de utilidades core que se importan
- Documentación esencial

## Components and Interfaces

### Files to Keep (Core Components)

1. **aurora_logging.py** - Sistema de logging utilizado por config-service
2. **__init__.py** - Archivo de inicialización del paquete
3. **README.md** - Documentación (actualizada para reflejar el estado actual)

### Files to Remove (Obsolete Components)

#### Cache and Build Files
- `__pycache__/` - Cache de Python
- `.pytest_cache/` - Cache de pytest
- Todos los archivos `.pyc`

#### Test and Demo Files
- `demo_test.py` - Script de demostración
- `simple_test.py` - Script de pruebas simple
- `test_*.py` - Archivos de prueba específicos
- `tests/` - Directorio completo de tests
- `TESTING_GUIDE.md` - Guía de testing

#### Service Generation Tools
- `generate_service.py` - Generador de servicios
- `templates/` - Directorio completo de templates
- `build.ps1` y `build.sh` - Scripts de build

#### Unused Core Files
- `base_app.py` - No usado por config-service
- `config.py` - Duplicado con app_config
- `database.py` - Config-service usa su propia implementación
- `errors.py` - No importado por config-service
- `events.py` - No usado en arquitectura actual
- `health_checks.py` - No usado por config-service
- `http_client.py` - No usado para comunicación inter-servicio
- `service_discovery.py` - No implementado en config-service
- `utils.py` - Funciones no utilizadas
- `sql_logging.py` - Funcionalidad específica ya integrada
- `config_loader.py` y `config_schemas.py` - Duplicados

#### Docker and Deployment Files
- `Dockerfile.base` - No usado en la arquitectura actual
- `requirements.txt` - Dependencias no necesarias

## Data Models

No aplica para esta limpieza, ya que no se modifican modelos de datos.

## Error Handling

### Validation Before Deletion
1. Verificar que config-service no importe directamente ningún archivo antes de eliminarlo
2. Hacer backup de archivos críticos antes de la eliminación
3. Probar que config-service sigue funcionando después de cada eliminación

### Rollback Strategy
- Mantener una lista de archivos eliminados
- Posibilidad de restaurar desde git si algo falla
- Verificación paso a paso del funcionamiento de config-service

## Testing Strategy

### Pre-cleanup Testing
1. Verificar que config-service funciona correctamente antes de la limpieza
2. Identificar todas las importaciones directas desde shared

### Post-cleanup Testing
1. Verificar que config-service sigue funcionando después de cada eliminación
2. Comprobar que no hay importaciones rotas
3. Validar que el logging sigue funcionando correctamente

### Validation Steps
1. Ejecutar config-service y verificar que inicia correctamente
2. Probar endpoints básicos del config-service
3. Verificar que los logs se generan correctamente
4. Confirmar que no hay errores de importación

## Implementation Phases

### Phase 1: Cache and Temporary Files
- Eliminar `__pycache__/` y `.pytest_cache/`
- Limpiar archivos `.pyc`

### Phase 2: Test and Demo Files
- Eliminar scripts de prueba y demo
- Remover directorio `tests/`

### Phase 3: Unused Core Components
- Eliminar archivos core no utilizados uno por uno
- Verificar config-service después de cada eliminación

### Phase 4: Service Generation Tools
- Eliminar herramientas de generación y templates

### Phase 5: Documentation Update
- Actualizar README.md para reflejar el estado actual
- Documentar qué archivos se mantuvieron y por qué