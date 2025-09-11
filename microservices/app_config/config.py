# app_config/config.py
from enum import Enum
from typing import NamedTuple, List, Optional

ServiceConfig = NamedTuple("ServiceConfig", [
    ("service_name", str),
    ("service_port", int),
    ("environment", str),
    ("debug", bool),
    ("log_level", str),
    ("cors_origins", List[str]),
    ("host", str),
])

DatabaseConfig = NamedTuple("DatabaseConfig", [
    ("host", str),
    ("port", int),
    ("user", str),
    ("password", str),
    ("database", str),
    ("charset", str),
    ("ssl_ca", Optional[str]),
])

Service = Enum('Service', [
    ('CONFIG', 'config'),
    ('FILE', 'file'),
    ('SUBJECT', 'subject'),
    ('SYLLABUS', 'syllabus'),
    ('AUTH', 'auth'),    
    ('NOTIFICATION', 'notification'),    
])

# Defaults específicos por servicio
DEFAULTS: dict[Service, dict[str, object]] = {
    Service.CONFIG: {
        "service_name": "config-service",
        "service_port": 8001,
        "environment": "development",
        "debug": False,
        "log_level": "INFO",
        "cors_origins": ["*"],
        "host": "127.0.0.1",
    },
    Service.FILE: {
        "service_name": "file-service",
        "service_port": 8002,
        "environment": "development",
        "debug": False,
        "log_level": "INFO",
        "cors_origins": ["http://localhost:3000"],
        "host": "127.0.0.1",
    },
    Service.SUBJECT: {
        "service_name": "subject-service",
        "service_port": 8003,
        "environment": "development",
        "debug": False,
        "log_level": "INFO",
        "cors_origins": ["*"],
        "host": "127.0.0.1",
    },
    Service.SYLLABUS: {
        "service_name": "syllabus-service",
        "service_port": 8004,
        "environment": "development",
        "debug": False,
        "log_level": "INFO",
        "cors_origins": ["*"],
        "host": "127.0.0.1",
    },
    Service.AUTH: {
        "service_name": "auth-service",
        "service_port": 8005,
        "environment": "development",
        "debug": False,
        "log_level": "INFO",
        "cors_origins": ["*"],
        "host": "127.0.0.1",
    },
}

DB_DEFAULTS: dict[Service, dict[str, object]] = {
    Service.CONFIG: {
        "host": "gateway01.us-east-1.prod.aws.tidbcloud.com",
        "port": 4000,
        "user": "3Eo7CXZzQYFQ3i5.root",
        "password": "sgCKlsXv6OhBfMta",
        "database": "config_db",
        "charset": "utf8mb4",
        "ssl_ca": "certs/tidb-ca-cert.pem",  # Ruta relativa al certificado
    },
    Service.FILE: {
        "host": "gateway01.us-east-1.prod.aws.tidbcloud.com",
        "port": 4000,
        "user": "3Eo7CXZzQYFQ3i5.root",
        "password": "sgCKlsXv6OhBfMta",
        "database": "file_db",
        "charset": "utf8mb4",
        "ssl_ca": "certs/tidb-ca-cert.pem",  # Mismo certificado
    },
    Service.SUBJECT: {
        "host": "gateway01.us-east-1.prod.aws.tidbcloud.com",
        "port": 4000,
        "user": "3Eo7CXZzQYFQ3i5.root",
        "password": "sgCKlsXv6OhBfMta",
        "database": "subject_db",
        "charset": "utf8mb4",
        "ssl_ca": "certs/tidb-ca-cert.pem",  # Mismo certificado
    },
    Service.SYLLABUS: {
        "host": "gateway01.us-east-1.prod.aws.tidbcloud.com",
        "port": 4000,
        "user": "3Eo7CXZzQYFQ3i5.root",
        "password": "sgCKlsXv6OhBfMta",
        "database": "syllabus_db",
        "charset": "utf8mb4",
        "ssl_ca": "certs/tidb-ca-cert.pem",  # Mismo certificado
    },
    Service.AUTH: {
        "host": "gateway01.us-east-1.prod.aws.tidbcloud.com",
        "port": 4000,
        "user": "3Eo7CXZzQYFQ3i5.root",
        "password": "sgCKlsXv6OhBfMta",
        "database": "auth_db",
        "charset": "utf8mb4",
        "ssl_ca": "certs/tidb-ca-cert.pem",  # Mismo certificado
    },
}

def parse_list(value: str | None, default: list[str]) -> list[str]:
    if value is None:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]

def get_service_config(env: dict[str, str], service: Service) -> ServiceConfig:
    prefix = service.value.upper()
    defaults = DEFAULTS[service]

    return ServiceConfig(
        service_name=env.get(f"{prefix}_SERVICE_NAME", defaults["service_name"]),
        service_port=int(env.get(f"{prefix}_SERVICE_PORT", str(defaults["service_port"]))),
        environment=env.get(f"{prefix}_ENVIRONMENT", defaults["environment"]),
        debug=env.get(f"{prefix}_DEBUG", str(defaults["debug"]).lower()).lower() == "true",
        log_level=env.get(f"{prefix}_LOG_LEVEL", defaults["log_level"]),
        cors_origins=parse_list(env.get(f"{prefix}_CORS_ORIGINS"), defaults["cors_origins"]),
        host=env.get(f"{prefix}_HOST", defaults["host"]),
    )

def get_ssl_path(ssl_ca: str | None) -> str | None:
    """Verifica y retorna la ruta válida del certificado SSL"""
    if not ssl_ca:
        return None
    
    import os
    
    # Intenta diferentes rutas posibles relativas a donde se ejecuta el servicio
    paths_to_try = [
        ssl_ca,
        f"../../{ssl_ca}",  # Desde un servicio específico hacia la raíz
        f"../../microservices/{ssl_ca}",  # Ruta compartida en microservices
        f"../shared/{ssl_ca}",  # Si tienes una carpeta shared
        f"./{ssl_ca}",
        f"microservices/{ssl_ca}",  # Desde la raíz del proyecto
        os.path.join(os.path.dirname(os.path.dirname(__file__)), ssl_ca),
    ]
    
    for path in paths_to_try:
        expanded_path = os.path.expanduser(path)
        absolute_path = os.path.abspath(expanded_path)
        if os.path.exists(absolute_path):
            return absolute_path
    
    # Si no encuentra el archivo, lanza una advertencia
    import warnings
    warnings.warn(f"SSL certificate not found at any of the expected paths for: {ssl_ca}")
    
    return ssl_ca  # Retorna el valor original si no encuentra el archivo

def get_database_config(env: dict[str, str], service: Service) -> DatabaseConfig:
    prefix = service.value.upper()
    defaults = DB_DEFAULTS[service]
    
    ssl_ca = env.get(f"{prefix}_DB_SSL_CA", defaults.get("ssl_ca"))
    
    return DatabaseConfig(
        host=env.get(f"{prefix}_DB_HOST", defaults["host"]),
        port=int(env.get(f"{prefix}_DB_PORT", str(defaults["port"]))),
        user=env.get(f"{prefix}_DB_USER", defaults["user"]),
        password=env.get(f"{prefix}_DB_PASSWORD", defaults["password"]),
        database=env.get(f"{prefix}_DB_DATABASE", defaults["database"]),
        charset=env.get(f"{prefix}_DB_CHARSET", defaults["charset"]),
        ssl_ca=get_ssl_path(ssl_ca),
    )

def namedtuple_to_connection_dict(config: DatabaseConfig) -> dict:
    """Convert DatabaseConfig to connection parameters dictionary"""
    return {k: v for k, v in config._asdict().items() if v is not None}