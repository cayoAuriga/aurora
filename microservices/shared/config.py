"""
Shared configuration utilities for Aurora microservices
"""
import os
from typing import Optional, Dict, Any, List
from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache


class DatabaseConfig(BaseSettings):
    """Database configuration"""
    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=3306, env="DB_PORT")
    username: str = Field(default="root", env="DB_USERNAME")
    password: str = Field(default="", env="DB_PASSWORD")
    database: str = Field(env="DB_DATABASE")
    ssl_ca: Optional[str] = Field(default=None, env="DB_SSL_CA")
    ssl_disabled: bool = Field(default=False, env="DB_SSL_DISABLED")
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    
    @property
    def connection_string(self) -> str:
        """Get database connection string"""
        ssl_args = ""
        if not self.ssl_disabled and self.ssl_ca:
            ssl_args = f"?ssl_ca={self.ssl_ca}&ssl_verify_cert=true&ssl_verify_identity=true"
        elif not self.ssl_disabled:
            ssl_args = "?ssl_mode=REQUIRED"
        
        return f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}{ssl_args}"


class RedisConfig(BaseSettings):
    """Redis configuration"""
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")
    ssl: bool = Field(default=False, env="REDIS_SSL")
    
    @property
    def connection_string(self) -> str:
        """Get Redis connection string"""
        protocol = "rediss" if self.ssl else "redis"
        auth = f":{self.password}@" if self.password else ""
        return f"{protocol}://{auth}{self.host}:{self.port}/{self.db}"


class ServiceDiscoveryConfig(BaseSettings):
    """Service discovery configuration"""
    enabled: bool = Field(default=True, env="SERVICE_DISCOVERY_ENABLED")
    consul_host: str = Field(default="localhost", env="CONSUL_HOST")
    consul_port: int = Field(default=8500, env="CONSUL_PORT")
    service_name: str = Field(env="SERVICE_NAME")
    service_host: str = Field(default="localhost", env="SERVICE_HOST")
    service_port: int = Field(env="SERVICE_PORT")
    health_check_interval: int = Field(default=10, env="HEALTH_CHECK_INTERVAL")


class BaseServiceConfig(BaseSettings):
    """Base configuration for all services"""
    service_name: str = Field(env="SERVICE_NAME")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    
    # Database
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    
    # Redis
    redis: RedisConfig = Field(default_factory=RedisConfig)
    
    # Service Discovery
    service_discovery: ServiceDiscoveryConfig = Field(default_factory=ServiceDiscoveryConfig)
    
    # API Gateway
    api_gateway_url: str = Field(default="http://localhost:8000", env="API_GATEWAY_URL")
    
    # Service URLs (for inter-service communication)
    subject_service_url: str = Field(default="http://localhost:8002", env="SUBJECT_SERVICE_URL")
    syllabus_service_url: str = Field(default="http://localhost:8001", env="SYLLABUS_SERVICE_URL")
    file_service_url: str = Field(default="http://localhost:8003", env="FILE_SERVICE_URL")
    config_service_url: str = Field(default="http://localhost:8004", env="CONFIG_SERVICE_URL")
    
    # Security
    jwt_secret_key: str = Field(default="your-secret-key", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # Rate limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class APIGatewayConfig(BaseServiceConfig):
    """API Gateway specific configuration"""
    service_name: str = "api-gateway"
    service_port: int = Field(default=8000, env="SERVICE_PORT")


class SubjectServiceConfig(BaseServiceConfig):
    """Subject Service specific configuration"""
    service_name: str = "subject-service"
    service_port: int = Field(default=8002, env="SERVICE_PORT")


class SyllabusServiceConfig(BaseServiceConfig):
    """Syllabus Service specific configuration"""
    service_name: str = "syllabus-service"
    service_port: int = Field(default=8001, env="SERVICE_PORT")


class FileServiceConfig(BaseServiceConfig):
    """File Service specific configuration"""
    service_name: str = "file-service"
    service_port: int = Field(default=8003, env="SERVICE_PORT")
    
    # File storage
    storage_provider: str = Field(default="local", env="STORAGE_PROVIDER")
    storage_path: str = Field(default="./uploads", env="STORAGE_PATH")
    max_file_size: int = Field(default=52428800, env="MAX_FILE_SIZE")  # 50MB
    allowed_file_types: List[str] = Field(
        default=["pdf", "doc", "docx", "txt", "md"],
        env="ALLOWED_FILE_TYPES"
    )


class ConfigServiceConfig(BaseServiceConfig):
    """Configuration Service specific configuration"""
    service_name: str = "config-service"
    service_port: int = Field(default=8004, env="SERVICE_PORT")


@lru_cache()
def get_config(service_name: str) -> BaseServiceConfig:
    """Get configuration for a specific service"""
    config_classes = {
        "api-gateway": APIGatewayConfig,
        "subject-service": SubjectServiceConfig,
        "syllabus-service": SyllabusServiceConfig,
        "file-service": FileServiceConfig,
        "config-service": ConfigServiceConfig,
    }
    
    config_class = config_classes.get(service_name, BaseServiceConfig)
    return config_class()


def load_env_file(env_file: str = ".env") -> None:
    """Load environment variables from file"""
    if os.path.exists(env_file):
        from dotenv import load_dotenv
        load_dotenv(env_file)


def get_service_url(service_name: str, config: BaseServiceConfig) -> str:
    """Get URL for a service"""
    service_urls = {
        "subject-service": config.subject_service_url,
        "syllabus-service": config.syllabus_service_url,
        "file-service": config.file_service_url,
        "config-service": config.config_service_url,
        "api-gateway": config.api_gateway_url,
    }
    
    return service_urls.get(service_name, f"http://localhost:8000")


def get_database_config(service_name: str) -> DatabaseConfig:
    """Get database configuration for a service"""
    # Each service has its own database
    database_names = {
        "api-gateway": "gateway_db",
        "subject-service": "subject_db",
        "syllabus-service": "syllabus_db",
        "file-service": "file_db",
        "config-service": "config_db",
    }
    
    config = DatabaseConfig()
    config.database = database_names.get(service_name, "aurora_db")
    return config