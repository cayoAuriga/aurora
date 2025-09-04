"""
Shared database utilities for Aurora microservices
"""
from typing import Optional, AsyncGenerator
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import contextmanager, asynccontextmanager
import logging

from .config import DatabaseConfig, get_database_config
from .aurora_logging import get_logger

logger = get_logger(__name__)

# Base class for all models
Base = declarative_base()

# Global database instances
_engines = {}
_session_makers = {}
_async_engines = {}
_async_session_makers = {}


def create_database_engine(config: DatabaseConfig, async_mode: bool = False):
    """Create database engine"""
    if async_mode:
        # For async, use aiomysql
        connection_string = config.connection_string.replace("mysql+pymysql://", "mysql+aiomysql://")
        engine = create_async_engine(
            connection_string,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            pool_timeout=config.pool_timeout,
            echo=config.database == "development"
        )
    else:
        engine = create_engine(
            config.connection_string,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            pool_timeout=config.pool_timeout,
            echo=config.database == "development"
        )
    
    return engine


def get_database_engine(service_name: str, async_mode: bool = False):
    """Get or create database engine for service"""
    cache_key = f"{service_name}_{async_mode}"
    
    if async_mode:
        if cache_key not in _async_engines:
            config = get_database_config(service_name)
            _async_engines[cache_key] = create_database_engine(config, async_mode=True)
        return _async_engines[cache_key]
    else:
        if cache_key not in _engines:
            config = get_database_config(service_name)
            _engines[cache_key] = create_database_engine(config, async_mode=False)
        return _engines[cache_key]


def get_session_maker(service_name: str, async_mode: bool = False):
    """Get or create session maker for service"""
    cache_key = f"{service_name}_{async_mode}"
    
    if async_mode:
        if cache_key not in _async_session_makers:
            engine = get_database_engine(service_name, async_mode=True)
            _async_session_makers[cache_key] = async_sessionmaker(
                engine, class_=AsyncSession, expire_on_commit=False
            )
        return _async_session_makers[cache_key]
    else:
        if cache_key not in _session_makers:
            engine = get_database_engine(service_name, async_mode=False)
            _session_makers[cache_key] = sessionmaker(
                bind=engine, autocommit=False, autoflush=False
            )
        return _session_makers[cache_key]


@contextmanager
def get_db_session(service_name: str) -> Session:
    """Get database session context manager"""
    SessionLocal = get_session_maker(service_name, async_mode=False)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


@asynccontextmanager
async def get_async_db_session(service_name: str) -> AsyncSession:
    """Get async database session context manager"""
    AsyncSessionLocal = get_session_maker(service_name, async_mode=True)
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Async database session error: {e}")
            raise


def get_db_dependency(service_name: str):
    """FastAPI dependency for database session"""
    def get_db():
        SessionLocal = get_session_maker(service_name, async_mode=False)
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    return get_db


def get_async_db_dependency(service_name: str):
    """FastAPI dependency for async database session"""
    async def get_async_db():
        AsyncSessionLocal = get_session_maker(service_name, async_mode=True)
        async with AsyncSessionLocal() as session:
            yield session
    
    return get_async_db


class BaseRepository:
    """Base repository class with common CRUD operations"""
    
    def __init__(self, session: Session, model_class):
        self.session = session
        self.model_class = model_class
    
    def create(self, **kwargs):
        """Create a new record"""
        instance = self.model_class(**kwargs)
        self.session.add(instance)
        self.session.flush()
        return instance
    
    def get_by_id(self, id: int):
        """Get record by ID"""
        return self.session.query(self.model_class).filter(
            self.model_class.id == id
        ).first()
    
    def get_all(self, skip: int = 0, limit: int = 100):
        """Get all records with pagination"""
        return self.session.query(self.model_class).offset(skip).limit(limit).all()
    
    def update(self, id: int, **kwargs):
        """Update record by ID"""
        instance = self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            self.session.flush()
        return instance
    
    def delete(self, id: int):
        """Delete record by ID"""
        instance = self.get_by_id(id)
        if instance:
            self.session.delete(instance)
            self.session.flush()
        return instance
    
    def exists(self, id: int) -> bool:
        """Check if record exists"""
        return self.session.query(self.model_class).filter(
            self.model_class.id == id
        ).first() is not None


class AsyncBaseRepository:
    """Async base repository class with common CRUD operations"""
    
    def __init__(self, session: AsyncSession, model_class):
        self.session = session
        self.model_class = model_class
    
    async def create(self, **kwargs):
        """Create a new record"""
        instance = self.model_class(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance
    
    async def get_by_id(self, id: int):
        """Get record by ID"""
        result = await self.session.execute(
            self.session.query(self.model_class).filter(
                self.model_class.id == id
            )
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100):
        """Get all records with pagination"""
        result = await self.session.execute(
            self.session.query(self.model_class).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def update(self, id: int, **kwargs):
        """Update record by ID"""
        instance = await self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await self.session.flush()
        return instance
    
    async def delete(self, id: int):
        """Delete record by ID"""
        instance = await self.get_by_id(id)
        if instance:
            await self.session.delete(instance)
            await self.session.flush()
        return instance
    
    async def exists(self, id: int) -> bool:
        """Check if record exists"""
        result = await self.session.execute(
            self.session.query(self.model_class).filter(
                self.model_class.id == id
            )
        )
        return result.scalar_one_or_none() is not None


def create_tables(service_name: str, metadata: MetaData):
    """Create database tables for service"""
    engine = get_database_engine(service_name, async_mode=False)
    metadata.create_all(bind=engine)
    logger.info(f"Created tables for service: {service_name}")


async def create_tables_async(service_name: str, metadata: MetaData):
    """Create database tables for service (async)"""
    engine = get_database_engine(service_name, async_mode=True)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    logger.info(f"Created tables for service: {service_name}")


def health_check(service_name: str) -> bool:
    """Check database health"""
    try:
        engine = get_database_engine(service_name, async_mode=False)
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed for {service_name}: {e}")
        return False


async def async_health_check(service_name: str) -> bool:
    """Check database health (async)"""
    try:
        engine = get_database_engine(service_name, async_mode=True)
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Async database health check failed for {service_name}: {e}")
        return False