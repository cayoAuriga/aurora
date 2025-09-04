"""
Tests for shared logging utilities
"""
import pytest
import logging
import json
from io import StringIO
import sys

from shared.aurora_logging import setup_logging, JSONFormatter, CorrelationIdFilter, log_request, log_event


def test_setup_logging():
    """Test logging setup"""
    logger = setup_logging("test-service", level="DEBUG", use_json=False)
    
    assert logger.name == "test-service"
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) > 0


def test_json_formatter():
    """Test JSON formatter"""
    formatter = JSONFormatter()
    
    # Create a log record
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None
    )
    record.service_name = "test-service"
    record.correlation_id = "test-123"
    
    # Format the record
    formatted = formatter.format(record)
    
    # Parse JSON
    log_data = json.loads(formatted)
    
    assert log_data["level"] == "INFO"
    assert log_data["service"] == "test-service"
    assert log_data["correlation_id"] == "test-123"
    assert log_data["message"] == "Test message"


def test_correlation_id_filter():
    """Test correlation ID filter"""
    correlation_id = "test-correlation-123"
    filter_obj = CorrelationIdFilter(correlation_id)
    
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    # Apply filter
    result = filter_obj.filter(record)
    
    assert result is True
    assert record.correlation_id == correlation_id


def test_log_request():
    """Test request logging"""
    # Capture log output
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JSONFormatter())
    
    logger = logging.getLogger("test-request")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    # Log a request
    log_request(
        logger=logger,
        method="GET",
        path="/api/test",
        status_code=200,
        response_time_ms=150.5,
        correlation_id="req-123"
    )
    
    # Check output
    output = stream.getvalue()
    assert "GET /api/test" in output
    assert "200" in output
    assert "150.5" in output


def test_log_event():
    """Test event logging"""
    # Capture log output
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JSONFormatter())
    
    logger = logging.getLogger("test-event")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    # Log an event
    log_event(
        logger=logger,
        event_type="user_created",
        event_data={"user_id": 123, "username": "test"},
        correlation_id="event-456"
    )
    
    # Check output
    output = stream.getvalue()
    assert "user_created" in output
    assert "event-456" in output


if __name__ == "__main__":
    pytest.main([__file__])