# database.py - Versión corregida para TiDB Cloud con SSL
import pymysql
from contextlib import contextmanager
from fastapi import HTTPException
from config import db_config
import sys
import os
# Add the parent directory to the path to import shared modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.aurora_logging import get_logger

logger = get_logger("config-service-db")


@contextmanager
def get_db_connection():
    """Get database connection with proper error handling"""
    connection = None
    try:
        connection = pymysql.connect(**db_config)
        yield connection
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
    finally:
        if connection:
            connection.close()