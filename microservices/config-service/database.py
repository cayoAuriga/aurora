# database.py
import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from config import db_config

# Configura logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Construye la URL de conexión para TiDB (sin exponer password en logs)
DATABASE_URL = (
    f"mysql+pymysql://{db_config['user']}:***@"  # ocultamos password
    f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
    f"?charset={db_config['charset']}"
)

# Debug logs
logger.info("========== Database Configuration ==========")
logger.info("Host: %s", db_config["host"])
logger.info("Port: %s", db_config["port"])
logger.info("User: %s", db_config["user"])
logger.info("Database: %s", db_config["database"])
logger.info("Charset: %s", db_config["charset"])
logger.info("SSL CA path: %s", db_config.get("ssl_ca"))
logger.info("Full DB URL (masked): %s", DATABASE_URL)
logger.info("============================================")

# Configura SSL solo si hay certificado
connect_args = {}
if db_config.get("ssl_ca"):
    connect_args["ssl"] = {"ca": db_config["ssl_ca"]}
    logger.info("SSL enabled with CA: %s", db_config["ssl_ca"])
else:
    logger.warning("⚠️ No SSL CA provided, attempting non-SSL connection")

# Usa la contraseña real solo para crear el engine
real_db_url = DATABASE_URL.replace("***", db_config["password"])

engine = create_engine(
    real_db_url,
    connect_args=connect_args,
    pool_pre_ping=True,   # Verifica conexiones antes de usarlas
    pool_recycle=300      # Recicla conexiones cada 5 min
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency para obtener la sesión de BD
def get_db() -> Generator[Session, None, None]:
    """Dependency que proporciona una sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# # database.py
# import pymysql
# from contextlib import contextmanager
# from fastapi import HTTPException
# from config import db_config
# import sys
# import os

# # Add the parent directory to the path to import shared modules
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# from shared.aurora_logging import get_logger

# logger = get_logger("config-service-db")


# @contextmanager
# def get_db_connection():
#     """Get database connection with proper error handling"""
#     connection = None
#     try:        
#         connection_params = db_config.copy()  # Copia para no modificar el original
        
#         # Manejo especial de SSL para TiDB
#         if 'ssl_ca' in connection_params and connection_params['ssl_ca']:
#             ssl_ca_path = connection_params.pop('ssl_ca')
#             if os.path.exists(ssl_ca_path):
#                 connection_params['ssl'] = {
#                     'ca': ssl_ca_path,
#                     'check_hostname': False
#                 }
#             else:
#                 logger.warning(f"SSL CA file not found at: {ssl_ca_path}")
#                 # TiDB Cloud requiere SSL
#                 connection_params['ssl_disabled'] = False
#         else:
#             # TiDB Cloud requiere SSL
#             connection_params['ssl_disabled'] = False
            
#         connection = pymysql.connect(**connection_params)
#         yield connection
        
#     except Exception as e:
#         logger.error(f"Database error: {e}")
#         raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
#     finally:
#         if connection:
#             connection.close()

# def init_database():
#     """Initialize database tables if they don't exist"""
#     try:
#         with get_db_connection() as conn:
#             cursor = conn.cursor()
            
#             # Create configurations table
#             cursor.execute("""
#                 CREATE TABLE IF NOT EXISTS app_configurations (
#                     id INT AUTO_INCREMENT PRIMARY KEY,
#                     config_key VARCHAR(255) NOT NULL,
#                     config_value TEXT NOT NULL,
#                     environment VARCHAR(50) NOT NULL DEFAULT 'development',
#                     service_name VARCHAR(100) NOT NULL DEFAULT 'global',
#                     description TEXT,
#                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
#                     UNIQUE KEY unique_config (config_key, environment, service_name)
#                 )
#             """)
            
#             # Create feature flags table
#             cursor.execute("""
#                 CREATE TABLE IF NOT EXISTS feature_flags (
#                     id INT AUTO_INCREMENT PRIMARY KEY,
#                     flag_name VARCHAR(255) NOT NULL,
#                     flag_key VARCHAR(255) NOT NULL,
#                     description TEXT,
#                     is_enabled BOOLEAN DEFAULT TRUE,
#                     rollout_percentage INT DEFAULT 100,
#                     environment VARCHAR(50) NOT NULL DEFAULT 'development',
#                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
#                     UNIQUE KEY unique_flag (flag_key, environment)
#                 )
#             """)
            
#             conn.commit()
#             logger.info("✅ Database tables initialized")
            
#     except Exception as e:
#         logger.error(f"⚠️  Database initialization error: {e}")
#         raise