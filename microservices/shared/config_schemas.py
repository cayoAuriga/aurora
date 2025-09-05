"""
Shared configuration schemas and validation utilities for Aurora microservices
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Any, Dict, List, Union
from datetime import datetime
from enum import Enum
import re


class EnvironmentType(str, Enum):
    """Standard environment types across all services"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ALL = "all"


class ServiceType(str, Enum):
    """Standard service types in the microservices architecture"""
    API_GATEWAY = "api-gateway"
    CONFIG_SERVICE = "config-service"
    SUBJECT_SERVICE = "subject-service"
    SYLLABUS_SERVICE = "syllabus-service"
    FILE_SERVICE = "file-service"


class ConfigurationType(str, Enum):
    """Types of configuration values"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"
    LIST = "list"


class ServiceRegistrationRequest(BaseModel):
    """Schema for service registration requests"""
    service_name: str = Field(..., min_length=1, max_length=50)
    host: str = Field(..., min_length=1, max_length=255)
    port: int = Field(..., ge=1, le=65535)
    health_endpoint: str = Field(default="/health", max_length=100)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('service_name')
    def validate_service_name(cls, v):
        if not re.match(r'^[a-z][a-z0-9-]*[a-z0-9]$', v):
            raise ValueError('Service name must be lowercase, start with letter, and contain only letters, numbers, and hyphens')
        return v
    
    @validator('health_endpoint')
    def validate_health_endpoint(cls, v):
        if not v.startswith('/'):
            raise ValueError('Health endpoint must start with /')
        return v


class ServiceRegistrationResponse(BaseModel):
    """Schema for service registration responses"""
    service_name: str
    host: str
    port: int
    health_endpoint: str
    status: str
    last_heartbeat: float
    metadata: Dict[str, Any]
    base_url: str
    health_url: str
    
    class Config:
        from_attributes = True


class HealthCheckRequest(BaseModel):
    """Schema for health check requests"""
    service_names: Optional[List[str]] = Field(None, description="Specific services to check, or all if None")
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    include_details: bool = Field(default=False, description="Include detailed health information")


class HealthCheckResponse(BaseModel):
    """Schema for health check responses"""
    service_name: str
    healthy: bool
    status: str
    timestamp: float
    response_time_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BulkHealthCheckResponse(BaseModel):
    """Schema for bulk health check responses"""
    results: Dict[str, HealthCheckResponse]
    summary: Dict[str, Any]
    timestamp: float


class ConfigurationValueRequest(BaseModel):
    """Schema for configuration value requests"""
    config_key: str = Field(..., min_length=1, max_length=100)
    environment: EnvironmentType = Field(default=EnvironmentType.ALL)
    service_name: Optional[str] = Field(None, max_length=50)
    default_value: Optional[Any] = Field(None)
    
    @validator('config_key')
    def validate_config_key(cls, v):
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9._-]*$', v):
            raise ValueError('Config key must start with letter and contain only alphanumeric, dots, underscores, hyphens')
        return v


class ConfigurationValueResponse(BaseModel):
    """Schema for configuration value responses"""
    key: str
    value: Any
    environment: str
    service_name: Optional[str]
    type: str
    is_sensitive: bool
    last_updated: datetime
    
    class Config:
        from_attributes = True


class BulkConfigurationRequest(BaseModel):
    """Schema for bulk configuration requests"""
    environment: EnvironmentType = Field(default=EnvironmentType.ALL)
    service_name: Optional[str] = Field(None, max_length=50)
    include_sensitive: bool = Field(default=False)
    keys_filter: Optional[List[str]] = Field(None, description="Specific keys to retrieve")


class BulkConfigurationResponse(BaseModel):
    """Schema for bulk configuration responses"""
    configurations: Dict[str, Any]
    total_count: int
    environment: str
    service_name: Optional[str]
    timestamp: float


class FeatureFlagCheckRequest(BaseModel):
    """Schema for feature flag check requests"""
    flag_key: str = Field(..., min_length=1, max_length=100)
    user_id: Optional[int] = Field(None, ge=1)
    environment: EnvironmentType = Field(default=EnvironmentType.ALL)
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context for flag evaluation")
    
    @validator('flag_key')
    def validate_flag_key(cls, v):
        if not re.match(r'^[a-z][a-z0-9_]*$', v):
            raise ValueError('Flag key must be lowercase, start with letter, and contain only letters, numbers, underscores')
        return v


class FeatureFlagCheckResponse(BaseModel):
    """Schema for feature flag check responses"""
    flag_key: str
    enabled: bool
    rollout_percentage: int
    user_qualified: bool
    reason: str
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ServiceDiscoveryQuery(BaseModel):
    """Schema for service discovery queries"""
    service_name: Optional[str] = Field(None, max_length=50)
    environment: Optional[EnvironmentType] = Field(None)
    healthy_only: bool = Field(default=True)
    include_metadata: bool = Field(default=False)


class ServiceDiscoveryResponse(BaseModel):
    """Schema for service discovery responses"""
    services: List[ServiceRegistrationResponse]
    total_count: int
    healthy_count: int
    timestamp: float


class ConfigurationValidationError(BaseModel):
    """Schema for configuration validation errors"""
    field: str
    error: str
    value: Any


class ValidationResponse(BaseModel):
    """Schema for validation responses"""
    valid: bool
    errors: List[ConfigurationValidationError] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


# Validation utilities
class ConfigurationValidator:
    """Utility class for configuration validation"""
    
    @staticmethod
    def validate_service_name(service_name: str) -> bool:
        """Validate service name format"""
        return bool(re.match(r'^[a-z][a-z0-9-]*[a-z0-9]$', service_name))
    
    @staticmethod
    def validate_config_key(config_key: str) -> bool:
        """Validate configuration key format"""
        return bool(re.match(r'^[a-zA-Z][a-zA-Z0-9._-]*$', config_key))
    
    @staticmethod
    def validate_flag_key(flag_key: str) -> bool:
        """Validate feature flag key format"""
        return bool(re.match(r'^[a-z][a-z0-9_]*$', flag_key))
    
    @staticmethod
    def validate_environment(environment: str) -> bool:
        """Validate environment value"""
        try:
            EnvironmentType(environment)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_port(port: int) -> bool:
        """Validate port number"""
        return 1 <= port <= 65535
    
    @staticmethod
    def validate_url_path(path: str) -> bool:
        """Validate URL path format"""
        return path.startswith('/') and len(path) <= 100
    
    @staticmethod
    def sanitize_config_value(value: Any, config_type: ConfigurationType) -> Any:
        """Sanitize and convert configuration value to appropriate type"""
        if value is None:
            return None
        
        try:
            if config_type == ConfigurationType.STRING:
                return str(value)
            elif config_type == ConfigurationType.INTEGER:
                return int(value)
            elif config_type == ConfigurationType.FLOAT:
                return float(value)
            elif config_type == ConfigurationType.BOOLEAN:
                if isinstance(value, bool):
                    return value
                if isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 'on')
                return bool(value)
            elif config_type == ConfigurationType.JSON:
                if isinstance(value, (dict, list)):
                    return value
                import json
                return json.loads(str(value))
            elif config_type == ConfigurationType.LIST:
                if isinstance(value, list):
                    return value
                if isinstance(value, str):
                    import json
                    return json.loads(value)
                return list(value)
            else:
                return value
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            raise ValueError(f"Cannot convert value '{value}' to type {config_type.value}: {e}")


# Standard configuration keys used across services
class StandardConfigKeys:
    """Standard configuration keys used across all services"""
    
    # Logging configuration
    LOG_LEVEL = "logging.level"
    LOG_FORMAT = "logging.format"
    LOG_OUTPUT = "logging.output"
    
    # Database configuration
    DB_CONNECTION_POOL_SIZE = "database.connection_pool.max_size"
    DB_CONNECTION_TIMEOUT = "database.connection_pool.timeout"
    DB_QUERY_TIMEOUT = "database.query_timeout"
    DB_SSL_ENABLED = "database.ssl.enabled"
    
    # HTTP client configuration
    HTTP_TIMEOUT = "http.client.timeout"
    HTTP_RETRY_COUNT = "http.client.retry_count"
    HTTP_RETRY_DELAY = "http.client.retry_delay"
    
    # Service discovery configuration
    SERVICE_DISCOVERY_ENABLED = "service_discovery.enabled"
    SERVICE_DISCOVERY_HEARTBEAT_INTERVAL = "service_discovery.heartbeat_interval"
    SERVICE_DISCOVERY_HEALTH_CHECK_TIMEOUT = "service_discovery.health_check_timeout"
    
    # CORS configuration
    CORS_ALLOWED_ORIGINS = "cors.allowed_origins"
    CORS_ALLOWED_METHODS = "cors.allowed_methods"
    CORS_ALLOWED_HEADERS = "cors.allowed_headers"
    
    # Rate limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE = "rate_limit.requests_per_minute"
    RATE_LIMIT_BURST_SIZE = "rate_limit.burst_size"
    
    # Circuit breaker
    CIRCUIT_BREAKER_FAILURE_THRESHOLD = "circuit_breaker.failure_threshold"
    CIRCUIT_BREAKER_TIMEOUT = "circuit_breaker.timeout"
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT = "circuit_breaker.recovery_timeout"


# Standard feature flags used across services
class StandardFeatureFlags:
    """Standard feature flags used across all services"""
    
    # Service features
    ENABLE_DETAILED_LOGGING = "enable_detailed_logging"
    ENABLE_METRICS_COLLECTION = "enable_metrics_collection"
    ENABLE_DISTRIBUTED_TRACING = "enable_distributed_tracing"
    
    # API features
    ENABLE_API_VERSIONING = "enable_api_versioning"
    ENABLE_REQUEST_VALIDATION = "enable_request_validation"
    ENABLE_RESPONSE_CACHING = "enable_response_caching"
    
    # Security features
    ENABLE_RATE_LIMITING = "enable_rate_limiting"
    ENABLE_CORS_VALIDATION = "enable_cors_validation"
    ENABLE_JWT_VALIDATION = "enable_jwt_validation"
    
    # Performance features
    ENABLE_CONNECTION_POOLING = "enable_connection_pooling"
    ENABLE_QUERY_OPTIMIZATION = "enable_query_optimization"
    ENABLE_ASYNC_PROCESSING = "enable_async_processing"
    
    # Experimental features
    ENABLE_NEW_API_ENDPOINTS = "enable_new_api_endpoints"
    ENABLE_BETA_FEATURES = "enable_beta_features"
    ENABLE_EXPERIMENTAL_CACHING = "enable_experimental_caching"