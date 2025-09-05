"""
Configuration loading utilities for Aurora microservices
"""
import os
import json
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class ServiceConfig:
    """Enhanced service configuration with remote config support"""
    service_name: str
    environment: str = "development"
    host: str = "localhost"
    service_port: int = 8000
    debug: bool = True
    log_level: str = "INFO"
    
    # Database configuration
    db_host: str = "localhost"
    db_port: int = 4000
    db_username: str = "root"
    db_password: str = ""
    db_database: str = ""
    db_ssl_ca: str = "ca-cert.pem"
    db_ssl_disabled: bool = False
    
    # Redis configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    
    # Service URLs
    api_gateway_url: str = "http://localhost:8000"
    config_service_url: str = "http://localhost:8004"
    
    # Security
    jwt_secret_key: str = "your-secret-key-change-in-production"
    
    # CORS
    cors_origins: list = field(default_factory=lambda: ["*"])
    
    # Remote configuration
    use_remote_config: bool = True
    config_cache_ttl: int = 300  # 5 minutes
    
    # Additional configurations loaded from remote
    remote_configs: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization setup"""
        # Set database name if not provided
        if not self.db_database:
            self.db_database = f"{self.service_name.replace('-', '_')}_db"
        
        # Load from environment variables
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        env_mappings = {
            "SERVICE_NAME": "service_name",
            "ENVIRONMENT": "environment",
            "HOST": "host",
            "SERVICE_PORT": ("service_port", int),
            "DEBUG": ("debug", lambda x: x.lower() in ["true", "1", "yes"]),
            "LOG_LEVEL": "log_level",
            
            "DB_HOST": "db_host",
            "DB_PORT": ("db_port", int),
            "DB_USERNAME": "db_username",
            "DB_PASSWORD": "db_password",
            "DB_DATABASE": "db_database",
            "DB_SSL_CA": "db_ssl_ca",
            "DB_SSL_DISABLED": ("db_ssl_disabled", lambda x: x.lower() in ["true", "1", "yes"]),
            
            "REDIS_HOST": "redis_host",
            "REDIS_PORT": ("redis_port", int),
            "REDIS_PASSWORD": "redis_password",
            
            "API_GATEWAY_URL": "api_gateway_url",
            "CONFIG_SERVICE_URL": "config_service_url",
            
            "JWT_SECRET_KEY": "jwt_secret_key",
            
            "USE_REMOTE_CONFIG": ("use_remote_config", lambda x: x.lower() in ["true", "1", "yes"]),
            "CONFIG_CACHE_TTL": ("config_cache_ttl", int),
        }
        
        for env_var, attr_info in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                if isinstance(attr_info, tuple):
                    attr_name, converter = attr_info
                    try:
                        setattr(self, attr_name, converter(env_value))
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Failed to convert {env_var}={env_value}: {e}")
                else:
                    setattr(self, attr_info, env_value)
        
        # Handle CORS origins
        cors_origins_env = os.getenv("CORS_ORIGINS")
        if cors_origins_env:
            try:
                self.cors_origins = json.loads(cors_origins_env)
            except json.JSONDecodeError:
                self.cors_origins = [origin.strip() for origin in cors_origins_env.split(",")]
    
    async def load_remote_configurations(self, config_client=None):
        """Load configurations from Configuration Service"""
        if not self.use_remote_config:
            return
        
        if config_client is None:
            from .service_discovery import get_config_client
            config_client = get_config_client()
        
        try:
            # Load bulk configurations for this service
            configs = await config_client.get_bulk_configurations(
                environment=self.environment,
                service_name=self.service_name
            )
            
            # Load global configurations
            global_configs = await config_client.get_bulk_configurations(
                environment=self.environment,
                service_name=None
            )
            
            # Merge configurations (service-specific overrides global)
            all_configs = {**global_configs, **configs}
            self.remote_configs = all_configs
            
            # Apply specific configurations to known attributes
            self._apply_remote_configs(all_configs)
            
            logger.info(f"Loaded {len(all_configs)} remote configurations")
            
        except Exception as e:
            logger.error(f"Failed to load remote configurations: {e}")
    
    def _apply_remote_configs(self, configs: Dict[str, Any]):
        """Apply remote configurations to service config attributes"""
        config_mappings = {
            "logging.level": "log_level",
            "cors.allowed_origins": "cors_origins",
            "database.connection_pool.max_size": None,  # Store in remote_configs
            "database.connection_pool.timeout": None,
        }
        
        for config_key, attr_name in config_mappings.items():
            if config_key in configs:
                value = configs[config_key]
                if attr_name:
                    setattr(self, attr_name, value)
                    logger.debug(f"Applied remote config {config_key} -> {attr_name}: {value}")
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value (remote configs take precedence)"""
        return self.remote_configs.get(key, default)
    
    def get_database_url(self) -> str:
        """Get database connection URL"""
        if self.db_ssl_disabled:
            return f"mysql+pymysql://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_database}"
        else:
            return f"mysql+pymysql://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_database}?ssl_ca={self.db_ssl_ca}&ssl_disabled=false"
    
    def get_redis_url(self) -> str:
        """Get Redis connection URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/0"
        else:
            return f"redis://{self.redis_host}:{self.redis_port}/0"


class ConfigurationManager:
    """Manages configuration loading and caching"""
    
    def __init__(self):
        self._configs: Dict[str, ServiceConfig] = {}
        self._config_client = None
    
    async def get_service_config(
        self,
        service_name: str,
        load_remote: bool = True
    ) -> ServiceConfig:
        """Get or create service configuration"""
        
        if service_name not in self._configs:
            # Create new configuration
            config = ServiceConfig(service_name=service_name)
            
            # Load remote configurations if enabled
            if load_remote and config.use_remote_config:
                await config.load_remote_configurations(self._get_config_client())
            
            self._configs[service_name] = config
        
        return self._configs[service_name]
    
    async def reload_config(self, service_name: str):
        """Reload configuration from remote source"""
        if service_name in self._configs:
            config = self._configs[service_name]
            if config.use_remote_config:
                await config.load_remote_configurations(self._get_config_client())
    
    def _get_config_client(self):
        """Get configuration client (lazy initialization)"""
        if self._config_client is None:
            from .service_discovery import get_config_client
            self._config_client = get_config_client()
        return self._config_client
    
    def clear_cache(self):
        """Clear configuration cache"""
        self._configs.clear()


# Global configuration manager
_config_manager = ConfigurationManager()


async def get_service_config(service_name: str, load_remote: bool = True) -> ServiceConfig:
    """Get service configuration (global function)"""
    return await _config_manager.get_service_config(service_name, load_remote)


async def reload_service_config(service_name: str):
    """Reload service configuration from remote source"""
    await _config_manager.reload_config(service_name)


def clear_config_cache():
    """Clear configuration cache"""
    _config_manager.clear_cache()


# Integration with existing config system
def get_enhanced_config_sync(service_name: str) -> ServiceConfig:
    """Get enhanced service configuration (synchronous, no remote loading)"""
    return ServiceConfig(service_name=service_name)