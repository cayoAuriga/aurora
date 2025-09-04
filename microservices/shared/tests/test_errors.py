"""
Tests for shared error handling
"""
import pytest
from datetime import datetime

from shared.errors import (
    BaseServiceException,
    ValidationError,
    NotFoundError,
    ConflictError,
    UnauthorizedError,
    ForbiddenError,
    ExternalServiceError,
    CircuitBreakerError,
    ErrorDetail,
    ErrorResponse,
    create_error_response,
    create_http_exception,
    handle_validation_errors
)


def test_base_service_exception():
    """Test base service exception"""
    exc = BaseServiceException(
        message="Test error",
        error_code="TEST_ERROR",
        status_code=400,
        correlation_id="test-123"
    )
    
    assert exc.message == "Test error"
    assert exc.error_code == "TEST_ERROR"
    assert exc.status_code == 400
    assert exc.correlation_id == "test-123"
    assert str(exc) == "Test error"


def test_validation_error():
    """Test validation error"""
    details = [
        ErrorDetail(field="name", message="Required field", code="required"),
        ErrorDetail(field="email", message="Invalid format", code="invalid_format")
    ]
    
    exc = ValidationError(
        message="Validation failed",
        details=details,
        correlation_id="val-123"
    )
    
    assert exc.error_code == "VALIDATION_ERROR"
    assert exc.status_code == 400
    assert len(exc.details) == 2
    assert exc.details[0].field == "name"


def test_not_found_error():
    """Test not found error"""
    exc = NotFoundError("User", "123", correlation_id="nf-123")
    
    assert exc.error_code == "RESOURCE_NOT_FOUND"
    assert exc.status_code == 404
    assert "User with id '123' not found" in exc.message


def test_conflict_error():
    """Test conflict error"""
    exc = ConflictError("Resource already exists", correlation_id="conf-123")
    
    assert exc.error_code == "RESOURCE_CONFLICT"
    assert exc.status_code == 409
    assert exc.message == "Resource already exists"


def test_unauthorized_error():
    """Test unauthorized error"""
    exc = UnauthorizedError(correlation_id="unauth-123")
    
    assert exc.error_code == "UNAUTHORIZED"
    assert exc.status_code == 401
    assert exc.message == "Unauthorized access"


def test_forbidden_error():
    """Test forbidden error"""
    exc = ForbiddenError(correlation_id="forb-123")
    
    assert exc.error_code == "FORBIDDEN"
    assert exc.status_code == 403
    assert exc.message == "Access forbidden"


def test_external_service_error():
    """Test external service error"""
    exc = ExternalServiceError("payment-service", "Connection timeout", correlation_id="ext-123")
    
    assert exc.error_code == "EXTERNAL_SERVICE_ERROR"
    assert exc.status_code == 502
    assert "payment-service" in exc.message
    assert "Connection timeout" in exc.message


def test_circuit_breaker_error():
    """Test circuit breaker error"""
    exc = CircuitBreakerError("user-service", correlation_id="cb-123")
    
    assert exc.error_code == "CIRCUIT_BREAKER_OPEN"
    assert exc.status_code == 503
    assert "user-service" in exc.message


def test_error_response():
    """Test error response model"""
    details = [ErrorDetail(field="name", message="Required", code="required")]
    
    response = ErrorResponse(
        error_code="TEST_ERROR",
        error_message="Test message",
        correlation_id="resp-123",
        timestamp=datetime.utcnow(),
        service_name="test-service",
        details=details
    )
    
    assert response.error_code == "TEST_ERROR"
    assert response.error_message == "Test message"
    assert response.service_name == "test-service"
    assert len(response.details) == 1


def test_create_error_response():
    """Test error response creation"""
    exc = ValidationError("Test validation error", correlation_id="create-123")
    response = create_error_response(exc, "test-service")
    
    assert response.error_code == "VALIDATION_ERROR"
    assert response.error_message == "Test validation error"
    assert response.service_name == "test-service"
    assert response.correlation_id == "create-123"


def test_create_http_exception():
    """Test HTTP exception creation"""
    exc = NotFoundError("User", "123", correlation_id="http-123")
    http_exc = create_http_exception(exc, "test-service")
    
    assert http_exc.status_code == 404
    assert isinstance(http_exc.detail, dict)
    assert http_exc.detail["error_code"] == "RESOURCE_NOT_FOUND"


def test_handle_validation_errors():
    """Test validation error handling"""
    pydantic_errors = [
        {"loc": ["name"], "msg": "field required", "type": "value_error.missing"},
        {"loc": ["email"], "msg": "invalid email format", "type": "value_error.email"}
    ]
    
    exc = handle_validation_errors(pydantic_errors)
    
    assert exc.error_code == "VALIDATION_ERROR"
    assert len(exc.details) == 2
    assert exc.details[0].field == "name"
    assert exc.details[1].field == "email"


if __name__ == "__main__":
    pytest.main([__file__])