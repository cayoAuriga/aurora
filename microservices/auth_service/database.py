# microservices/auth_service/database.py
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Generator
from pymongo import MongoClient
from pymongo.database import Database as MongoDatabase
from shared.aurora_logging import get_logger
from shared.sql_logging import setup_sql_logging
from shared.settings import get_database_config, get_mongo_config, Service

# ===============================
#   Configuración del servicio
# ===============================
db_config = get_database_config(Service.AUTH)
logger = get_logger("auth-service")
logger.info(db_config)

# ===============================
#   URL de conexión MySQL/TiDB
# ===============================
DATABASE_URL = (
    f"mysql+pymysql://{db_config.user}:{db_config.password}"
    f"@{db_config.host}:{db_config.port}/{db_config.database}"
    f"?charset={db_config.charset}"
)

logger.info("========== MySQL/TiDB Configuration ==========")
logger.info("Host: %s", db_config.host)
logger.info("Port: %s", db_config.port)
logger.info("User: %s", db_config.user)
logger.info("Database: %s", db_config.database)
logger.info("Full DB URL (masked): %s", DATABASE_URL.replace(db_config.password, "***"))
logger.info("============================================")

# ===============================
#   Engine y Session SQLAlchemy
# ===============================
connect_args = {}
if db_config.ssl_ca:
    connect_args["ssl"] = {"ca": db_config.ssl_ca}
    logger.info("SSL enabled with CA: %s", db_config.ssl_ca)
else:
    logger.warning("⚠️ SSL disabled or not provided")

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False,
    future=True
)

# Logging de SQL
setup_sql_logging(engine)

@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    logger.info("🟡 Ejecutando SQL:\n   %s", statement)
    logger.debug("➡️ Parámetros: %s", parameters)

@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    if cursor.description:
        logger.info("✅ Query devolvió %s filas", cursor.rowcount)
    else:
        logger.info("✅ Query ejecutada sin devolución de filas (INSERT/UPDATE/DELETE)")

# ORM Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Dependency que proporciona sesión SQLAlchemy"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("Error en la sesión de DB: %s", e)
        db.rollback()
        raise
    finally:
        db.close()

# ===============================
#   Configuración MongoDB Atlas
# ===============================
mongo_config = get_mongo_config(Service.AUTH)

logger.info("========== MongoDB Configuration ==========")
logger.info("Database: %s", mongo_config.database)
logger.info("============================================")

try:
    mongo_client = MongoClient(mongo_config.uri)
    # Ping para verificar la conexión al iniciar
    mongo_client.admin.command('ping')
    logger.info("✅ MongoDB connection successful.")
except Exception as e:
    logger.error("❌ Failed to connect to MongoDB: %s", e)
    raise

mongo_db = mongo_client[mongo_config.database]

def get_mongo_db() -> Generator[MongoDatabase, None, None]:
    """Dependency que proporciona la instancia de la base de datos MongoDB."""
    try:
        yield mongo_db
    except Exception as e:
        logger.error("Error en la sesión de MongoDB: %s", e)
        raise
    # MongoClient gestiona el pool de conexiones, no es necesario cerrarlo aquí.