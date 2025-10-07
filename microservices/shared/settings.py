# /microservices/shared/settings.py
import os
from enum import Enum
from typing import List, Optional # Optional es un alias común para Union[T, None]
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from enum import Enum

class Service(str, Enum):
    CONFIG = "config"
    AUTH = "auth"
    FILE = "file"
    SUBJECT = "subject"
    SYLLABUS = "syllabus"

# 1. Añade un modelo para la configuración de MongoDB
class MongoConfig(BaseModel):
    uri: str
    database: str

# 2. Implementa la función get_mongo_config
def get_mongo_config(service: Service) -> MongoConfig:
    """Carga la configuración de MongoDB desde variables de entorno."""
    
    # Usaremos prefijos para las variables si es necesario, 
    # pero para este ejemplo usaremos nombres genéricos.
    # En una arquitectura más compleja, podrías usar algo como AUTH_MONGO_URI
    
    mongo_uri = os.getenv("MONGO_URI")
    mongo_database = os.getenv("MONGO_DATABASE")

    if not mongo_uri or not mongo_database:
        raise ValueError(
            "MONGO_URI and MONGO_DATABASE environment variables must be set."
        )

    return MongoConfig(uri=mongo_uri, database=mongo_database)


# Heredamos de BaseSettings en lugar de BaseModel
class ServiceConfig(BaseSettings):
    # Pydantic-settings buscará una variable de entorno con este prefijo
    model_config = SettingsConfigDict(env_prefix='', extra='ignore')

    # Los valores por defecto se definen directamente en el modelo
    service_name: str
    service_port: int = 8000
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    cors_origins: List[str] = ["*"]
    host: str = "127.0.0.1"

class DatabaseConfig(BaseSettings):
    # El prefijo se define aquí, Pydantic hará el resto
    model_config = SettingsConfigDict(env_prefix='', extra='ignore')

    host: str
    port: int = 4000
    user: str
    password: str
    database: str
    charset: str = "utf8mb4"
    ssl_ca: Optional[str] = None # Usando Optional para mayor claridad

class MongoConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='', extra='ignore')
    
    uri: str
    database: str



def get_service_config(service: Service) -> ServiceConfig:
    """Carga la configuración base para un servicio específico."""
    prefix = service.value.upper()
    
    # pydantic-settings buscará variables como AUTH_SERVICE_PORT, etc.
    config = ServiceConfig(_env_prefix=f"{prefix}_")
    
    # Asignamos el nombre del servicio manualmente
    config.service_name = f"{service.value}-service"
    return config

def get_database_config(service: Service) -> DatabaseConfig:
    """Carga la configuración de la base de datos para un servicio específico."""
    prefix = service.value.upper()
    
    # pydantic-settings buscará AUTH_DB_HOST, AUTH_DB_PORT, etc.
    return DatabaseConfig(_env_prefix=f"{prefix}_DB_")

class GoogleOAuthConfig(BaseModel):
    client_id: str
    client_secret: str
    redirect_uri: str
    token_url: str = "https://oauth2.googleapis.com/token"
    userinfo_url: str = "https://openidconnect.googleapis.com/v1/userinfo"

def get_google_oauth_config() -> GoogleOAuthConfig:
    """Carga la configuración de Google OAuth desde variables de entorno."""
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")

    if not all([client_id, client_secret, redirect_uri]):
        raise ValueError("GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GOOGLE_REDIRECT_URI must be set.")
    
    return GoogleOAuthConfig(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
    )
