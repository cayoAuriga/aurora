"""
Shared event schemas and utilities for Aurora microservices
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
import uuid


class EventType(str, Enum):
    """Standard event types"""
    # Subject events
    SUBJECT_CREATED = "subject.created"
    SUBJECT_UPDATED = "subject.updated"
    SUBJECT_DELETED = "subject.deleted"
    
    # Syllabus events
    SYLLABUS_CREATED = "syllabus.created"
    SYLLABUS_UPDATED = "syllabus.updated"
    SYLLABUS_DELETED = "syllabus.deleted"
    SYLLABUS_PUBLISHED = "syllabus.published"
    
    # File events
    FILE_UPLOADED = "file.uploaded"
    FILE_DELETED = "file.deleted"
    REPOSITORY_SYNCED = "repository.synced"
    
    # User events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    
    # Configuration events
    CONFIG_UPDATED = "config.updated"
    FEATURE_FLAG_TOGGLED = "feature_flag.toggled"


class DomainEvent(BaseModel):
    """Base domain event model"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    aggregate_id: str
    aggregate_type: str
    event_data: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: str
    service_name: str
    version: int = 1
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Subject Events
class SubjectCreatedEvent(DomainEvent):
    """Subject created event"""
    event_type: EventType = EventType.SUBJECT_CREATED
    aggregate_type: str = "subject"


class SubjectUpdatedEvent(DomainEvent):
    """Subject updated event"""
    event_type: EventType = EventType.SUBJECT_UPDATED
    aggregate_type: str = "subject"


class SubjectDeletedEvent(DomainEvent):
    """Subject deleted event"""
    event_type: EventType = EventType.SUBJECT_DELETED
    aggregate_type: str = "subject"


# Syllabus Events
class SyllabusCreatedEvent(DomainEvent):
    """Syllabus created event"""
    event_type: EventType = EventType.SYLLABUS_CREATED
    aggregate_type: str = "syllabus"


class SyllabusUpdatedEvent(DomainEvent):
    """Syllabus updated event"""
    event_type: EventType = EventType.SYLLABUS_UPDATED
    aggregate_type: str = "syllabus"


class SyllabusDeletedEvent(DomainEvent):
    """Syllabus deleted event"""
    event_type: EventType = EventType.SYLLABUS_DELETED
    aggregate_type: str = "syllabus"


class SyllabusPublishedEvent(DomainEvent):
    """Syllabus published event"""
    event_type: EventType = EventType.SYLLABUS_PUBLISHED
    aggregate_type: str = "syllabus"


# File Events
class FileUploadedEvent(DomainEvent):
    """File uploaded event"""
    event_type: EventType = EventType.FILE_UPLOADED
    aggregate_type: str = "file"


class FileDeletedEvent(DomainEvent):
    """File deleted event"""
    event_type: EventType = EventType.FILE_DELETED
    aggregate_type: str = "file"


class RepositorySyncedEvent(DomainEvent):
    """Repository synced event"""
    event_type: EventType = EventType.REPOSITORY_SYNCED
    aggregate_type: str = "repository"


# User Events
class UserCreatedEvent(DomainEvent):
    """User created event"""
    event_type: EventType = EventType.USER_CREATED
    aggregate_type: str = "user"


class UserUpdatedEvent(DomainEvent):
    """User updated event"""
    event_type: EventType = EventType.USER_UPDATED
    aggregate_type: str = "user"


class UserDeletedEvent(DomainEvent):
    """User deleted event"""
    event_type: EventType = EventType.USER_DELETED
    aggregate_type: str = "user"


# Configuration Events
class ConfigUpdatedEvent(DomainEvent):
    """Configuration updated event"""
    event_type: EventType = EventType.CONFIG_UPDATED
    aggregate_type: str = "configuration"


class FeatureFlagToggledEvent(DomainEvent):
    """Feature flag toggled event"""
    event_type: EventType = EventType.FEATURE_FLAG_TOGGLED
    aggregate_type: str = "feature_flag"


class EventPublisher:
    """Base event publisher interface"""
    
    async def publish(self, event: DomainEvent) -> None:
        """Publish an event"""
        raise NotImplementedError
    
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """Publish multiple events"""
        raise NotImplementedError


class EventSubscriber:
    """Base event subscriber interface"""
    
    def __init__(self, event_types: List[EventType]):
        self.event_types = event_types
    
    async def handle_event(self, event: DomainEvent) -> None:
        """Handle an incoming event"""
        raise NotImplementedError
    
    def can_handle(self, event_type: EventType) -> bool:
        """Check if this subscriber can handle the event type"""
        return event_type in self.event_types


def create_event(
    event_type: EventType,
    aggregate_id: str,
    aggregate_type: str,
    event_data: Dict[str, Any],
    correlation_id: str,
    service_name: str,
    metadata: Optional[Dict[str, Any]] = None
) -> DomainEvent:
    """Create a domain event"""
    return DomainEvent(
        event_type=event_type,
        aggregate_id=aggregate_id,
        aggregate_type=aggregate_type,
        event_data=event_data,
        correlation_id=correlation_id,
        service_name=service_name,
        metadata=metadata or {}
    )


def create_subject_created_event(
    subject_id: str,
    subject_data: Dict[str, Any],
    correlation_id: str,
    service_name: str = "subject-service"
) -> SubjectCreatedEvent:
    """Create a subject created event"""
    return SubjectCreatedEvent(
        aggregate_id=subject_id,
        event_data=subject_data,
        correlation_id=correlation_id,
        service_name=service_name
    )


def create_syllabus_created_event(
    syllabus_id: str,
    syllabus_data: Dict[str, Any],
    correlation_id: str,
    service_name: str = "syllabus-service"
) -> SyllabusCreatedEvent:
    """Create a syllabus created event"""
    return SyllabusCreatedEvent(
        aggregate_id=syllabus_id,
        event_data=syllabus_data,
        correlation_id=correlation_id,
        service_name=service_name
    )


def create_file_uploaded_event(
    file_id: str,
    file_data: Dict[str, Any],
    correlation_id: str,
    service_name: str = "file-service"
) -> FileUploadedEvent:
    """Create a file uploaded event"""
    return FileUploadedEvent(
        aggregate_id=file_id,
        event_data=file_data,
        correlation_id=correlation_id,
        service_name=service_name
    )