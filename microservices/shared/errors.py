"""
Shared error handling utilities for Aurora microservices
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import HTTPException
from pydantic import BaseModel
import uuid


class ErrorDetail(BaseModel):
    """Error detail model"""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standardized error response model"""
    error_code: str
    error_message: str
    correlation_id: str
    timestamp: datetime
    service_name: str
    details: Optional[List[ErrorDetail]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BaseServiceException(Exception):
    """Base exception for all service exceptions"""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        details: Optional[List[ErrorDetail]] = None,
        correlation_id: Optional[str] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or []
        self.correlation_id = correlation_id or str(uuid.uuid4())
        super().__init__(message)


class ValidationError(BaseServiceException):
    """Validation error exception"""
    
    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[List[ErrorDetail]] = None,
        correlation_id: Optional[str] = None
    ):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details,
            correlation_id=correlation_id
        )


class NotFoundError(BaseServiceException):
    """Resource not found exception"""
    
    def __init__(
        self,
        resource: str,
        resource_id: str,
        correlation_id: Optional[str] = None
    ):
        message = f"{resource} with id '{resource_id}' not found"
        super().__init__(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            status_code=404,
            correlation_id=correlation_id
        )


class ConflictError(BaseServiceException):
    """Resource conflict exception"""
    
    def __init__(
        self,
        message: str,
        correlation_id: Optional[str] = None
    ):
        super().__init__(
            message=message,
            error_code="RESOURCE_CONFLICT",
            status_code=409,
            correlation_id=correlation_id
        )


class UnauthorizedError(BaseServiceException):
    """Unauthorized access exception"""
    
    def __init__(
        self,
        message: str = "Unauthorized access",
        correlation_id: Optional[str] = None
    ):
        super().__init__(
            message=message,
            error_code="UNAUTHORIZED",
            status_code=401,
            correlation_id=correlation_id
        )


class ForbiddenError(BaseServiceException):
    """Forbidden access exception"""
    
    def __init__(
        self,
        message: str = "Access forbidden",
        correlation_id: Optional[str] = None
    ):
        super().__init__(
            message=message,
            error_code="FORBIDDEN",
            status_code=403,
            correlation_id=correlation_id
        )


class ExternalServiceError(BaseServiceException):
    """External service error exception"""
    
    def __init__(
        self,
        service_name: str,
        message: str,
        correlation_id: Optional[str] = None
    ):
        super().__init__(
            message=f"External service '{service_name}' error: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            correlation_id=correlation_id
        )


class CircuitBreakerError(BaseServiceException):
    """Circuit breaker open exception"""
    
    def __init__(
        self,
        service_name: str,
        correlation_id: Optional[str] = None
    ):
        message = f"Circuit breaker is open for service '{service_name}'"
        super().__init__(
            message=message,
            error_code="CIRCUIT_BREAKER_OPEN",
            status_code=503,
            correlation_id=correlation_id
        )


def create_error_response(
    exception: BaseServiceException,
    service_name: str
) -> ErrorResponse:
    """Create standardized error response from exception"""
    return ErrorResponse(
        error_code=exception.error_code,
        error_message=exception.message,
        correlation_id=exception.correlation_id,
        timestamp=datetime.utcnow(),
        service_name=service_name,
        details=exception.details
    )


def create_http_exception(
    exception: BaseServiceException,
    service_name: str
) -> HTTPException:
    """Create FastAPI HTTPException from service exception"""
    error_response = create_error_response(exception, service_name)
    return HTTPException(
        status_code=exception.status_code,
        detail=error_response.dict()
    )


def handle_validation_errors(errors: List[Dict[str, Any]]) -> ValidationError:
    """Convert Pydantic validation errors to ValidationError"""
    details = []
    for error in errors:
        field = ".".join(str(loc) for loc in error.get("loc", []))
        details.append(ErrorDetail(
            field=field,
            message=error.get("msg", "Validation error"),
            code=error.get("type")
        ))
    
    return ValidationError(
        message="Request validation failed",
        details=details
    )