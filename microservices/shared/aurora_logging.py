"""
Shared logging utilities for Aurora microservices
"""
import logging
import json
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


class CorrelationIdFilter(logging.Filter):
    """Filter to add correlation ID to log records"""
    
    def __init__(self, correlation_id: Optional[str] = None):
        super().__init__()
        self.correlation_id = correlation_id or str(uuid.uuid4())
    
    def filter(self, record):
        record.correlation_id = self.correlation_id
        return True


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": getattr(record, 'service_name', 'unknown'),
            "correlation_id": getattr(record, 'correlation_id', ''),
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 
                          'exc_text', 'stack_info', 'correlation_id', 'service_name']:
                log_entry[key] = value
        
        return json.dumps(log_entry)


def setup_logging(
    service_name: str,
    level: str = "INFO",
    correlation_id: Optional[str] = None,
    use_json: bool = True
) -> logging.Logger:
    """
    Set up logging for a microservice
    
    Args:
        service_name: Name of the service
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        correlation_id: Optional correlation ID for request tracing
        use_json: Whether to use JSON formatting
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    if use_json:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(correlation_id)s - %(message)s'
        )
    
    handler.setFormatter(formatter)
    
    # Add correlation ID filter
    correlation_filter = CorrelationIdFilter(correlation_id)
    handler.addFilter(correlation_filter)
    
    # Add service name to all records
    class ServiceNameFilter(logging.Filter):
        def filter(self, record):
            record.service_name = service_name
            return True
    
    handler.addFilter(ServiceNameFilter())
    
    logger.addHandler(handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


def log_request(logger: logging.Logger, method: str, path: str, status_code: int, 
                response_time_ms: float, correlation_id: str, **kwargs):
    """Log HTTP request details"""
    logger.info(
        f"{method} {path} - {status_code} - {response_time_ms}ms",
        extra={
            "event_type": "http_request",
            "method": method,
            "path": path,
            "status_code": status_code,
            "response_time_ms": response_time_ms,
            "correlation_id": correlation_id,
            **kwargs
        }
    )


def log_event(logger: logging.Logger, event_type: str, event_data: Dict[str, Any], 
              correlation_id: str, **kwargs):
    """Log domain events"""
    logger.info(
        f"Event: {event_type}",
        extra={
            "event_type": event_type,
            "event_data": event_data,
            "correlation_id": correlation_id,
            **kwargs
        }
    )