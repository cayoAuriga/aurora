"""
Shared logging utilities for microservices
"""
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


class StructuredLogger:
    """Structured logger with correlation ID support"""
    
    def __init__(self, service_name: str, correlation_id: Optional[str] = None):
        self.service_name = service_name
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.logger = logging.getLogger(service_name)
        
        # Configure structured logging format
        handler = logging.StreamHandler()
        formatter = StructuredFormatter()
        handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _log(self, level: str, message: str, extra: Optional[Dict[str, Any]] = None):
        """Internal logging method with structured format"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "correlation_id": self.correlation_id,
            "level": level,
            "message": message
        }
        
        if extra:
            log_data.update(extra)
        
        getattr(self.logger, level.lower())(json.dumps(log_data))
    
    def info(self, message: str, **kwargs):
        self._log("INFO", message, kwargs)
    
    def error(self, message: str, **kwargs):
        self._log("ERROR", message, kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log("WARNING", message, kwargs)
    
    def debug(self, message: str, **kwargs):
        self._log("DEBUG", message, kwargs)


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging"""
    
    def format(self, record):
        return record.getMessage()


def get_logger(service_name: str, correlation_id: Optional[str] = None) -> StructuredLogger:
    """Factory function to get a structured logger instance"""
    return StructuredLogger(service_name, correlation_id)