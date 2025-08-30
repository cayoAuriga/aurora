"""
Shared utilities package for microservices
"""
from .logging import get_logger, StructuredLogger
from .error_handling import (
    ErrorResponse, 
    ServiceException, 
    ValidationException, 
    NotFoundError, 
    ServiceUnavailableError,
    create_http_exception
)
from .event_schemas import (
    DomainEvent,
    EventType,
    EventPublisher,
    SyllabusCreatedEvent,
    SyllabusUpdatedEvent,
    SyllabusDeletedEvent,
    SubjectCreatedEvent,
    SubjectUpdatedEvent,
    SubjectDeletedEvent,
    FileUploadedEvent,
    FileDeletedEvent
)

__all__ = [
    "get_logger",
    "StructuredLogger",
    "ErrorResponse",
    "ServiceException",
    "ValidationException", 
    "NotFoundError",
    "ServiceUnavailableError",
    "create_http_exception",
    "DomainEvent",
    "EventType",
    "EventPublisher",
    "SyllabusCreatedEvent",
    "SyllabusUpdatedEvent", 
    "SyllabusDeletedEvent",
    "SubjectCreatedEvent",
    "SubjectUpdatedEvent",
    "SubjectDeletedEvent",
    "FileUploadedEvent",
    "FileDeletedEvent"
]