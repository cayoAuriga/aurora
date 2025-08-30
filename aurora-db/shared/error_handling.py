"""
Shared error handling utilities for microservices
"""
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException
from pydantic import BaseModel
import uuid


class ErrorResponse(BaseModel):
    """Standardized error response model"""
    error_code: str
    error_message: str
    correlation_id: str
    timestamp: str
    service_name: str
    details: Optional[Dict[str, Any]] = None


class ServiceException(Exception):
    """Base exception class for service-specific errors"""
    
    def __init__(
        self, 
        message: str, 
        error_code: str, 
        service_name: str,
        correlation_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.service_name = service_name
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.details = details or {}
        super().__init__(self.message)
    
    def to_error_response(self) -> ErrorResponse:
        """Convert exception to standardized error response"""
        return ErrorResponse(
            error_code=self.error_code,
            error_message=self.message,
            correlation_id=self.correlation_id,
            timestamp=datetime.utcnow().isoformat(),
            service_name=self.service_name,
            details=self.details
        )


class ValidationException(ServiceException):
    """Exception for validation errors"""
    
    def __init__(self, message: str, service_name: str, field_errors: Optional[Dict] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            service_name=service_name,
            details={"field_errors": field_errors or {}},
            **kwargs
        )


class NotFoundError(ServiceException):
    """Exception for resource not found errors"""
    
    def __init__(self, resource_type: str, resource_id: str, service_name: str, **kwargs):
        super().__init__(
            message=f"{resource_type} with id {resource_id} not found",
            error_code="RESOURCE_NOT_FOUND",
            service_name=service_name,
            details={"resource_type": resource_type, "resource_id": resource_id},
            **kwargs
        )


class ServiceUnavailableError(ServiceException):
    """Exception for service unavailable errors"""
    
    def __init__(self, target_service: str, service_name: str, **kwargs):
        super().__init__(
            message=f"Service {target_service} is currently unavailable",
            error_code="SERVICE_UNAVAILABLE",
            service_name=service_name,
            details={"target_service": target_service},
            **kwargs
        )


def create_http_exception(service_exception: ServiceException, status_code: int = 500) -> HTTPException:
    """Convert ServiceException to FastAPI HTTPException"""
    return HTTPException(
        status_code=status_code,
        detail=service_exception.to_error_response().dict()
    )