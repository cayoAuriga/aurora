# /microservices/shared/settings.py
import os
from dotenv import load_dotenv
from typing import List, Optional
from collections import namedtuple
from enum import Enum

load_dotenv()  # carga el archivo .env

class Service(str, Enum):
    CONFIG = "config",
    AUTH = "auth",
    FILE = "file"
    SUBJECT = "subject"
    SYLLABUS = "syllabus"   

ServiceConfig = namedtuple("ServiceConfig", [
    "service_name", "service_port", "environment", "debug",
    "log_level", "cors_origins", "host"
])

DatabaseConfig = namedtuple("DatabaseConfig", [
    "host", "port", "user", "password", "database", "charset", "ssl_ca"
])
MongoConfig = namedtuple("MongoConfig", [
    "uri", "database"
])

def get_service_config(service: Service) -> ServiceConfig:
    prefix = service.value.upper()
    return ServiceConfig(
        service_name=f"{service.value}-service",
        service_port=int(os.getenv(f"{prefix}_SERVICE_PORT", 8000)),
        environment=os.getenv("ENVIRONMENT", "development"),
        debug=os.getenv("DEBUG", "False").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        cors_origins=os.getenv("CORS_ORIGINS", "*").split(","),
        host=os.getenv(f"{prefix}_SERVICE_HOST", "127.0.0.1"),
    )

def get_database_config(service: Service) -> DatabaseConfig:
    prefix = service.value.upper()
    return DatabaseConfig(
        host=os.getenv(f"{prefix}_DB_HOST"),
        port=int(os.getenv(f"{prefix}_DB_PORT", "4000")),
        user=os.getenv(f"{prefix}_DB_USER"),
        password=os.getenv(f"{prefix}_DB_PASSWORD"),
        database=os.getenv(f"{prefix}_DB_NAME"),
        charset=os.getenv(f"{prefix}_DB_CHARSET", "utf8mb4"),
        ssl_ca=os.getenv(f"{prefix}_DB_SSL_CA", None),
    )
def get_mongo_config(service: Service) -> MongoConfig:
    prefix = service.value.upper()
    return MongoConfig(
        uri=os.getenv(f"{prefix}_MONGO_URI"),
        database=os.getenv(f"{prefix}_MONGO_DB"),
    )