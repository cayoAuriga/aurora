"""
Shared event schemas for microservices communication
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
import uuid


class EventType(str, Enum):
    """Enumeration of domain event types"""
    # Syllabus events
    SYLLABUS_CREATED = "syllabus.created"
    SYLLABUS_UPDATED = "syllabus.updated"
    SYLLABUS_DELETED = "syllabus.deleted"
    
    # Subject events
    SUBJECT_CREATED = "subject.created"
    SUBJECT_UPDATED = "subject.updated"
    SUBJECT_DELETED = "subject.deleted"
    
    # File events
    FILE_UPLOADED = "file.uploaded"
    FILE_DELETED = "file.deleted"


class DomainEvent(BaseModel):
    """Base domain event schema"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    aggregate_id: str
    aggregate_type: str
    event_data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: str
    version: int = 1
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Syllabus Event Schemas
class SyllabusCreatedEvent(DomainEvent):
    """Event published when a syllabus is created"""
    event_type: EventType = EventType.SYLLABUS_CREATED
    aggregate_type: str = "syllabus"


class SyllabusUpdatedEvent(DomainEvent):
    """Event published when a syllabus is updated"""
    event_type: EventType = EventType.SYLLABUS_UPDATED
    aggregate_type: str = "syllabus"


class SyllabusDeletedEvent(DomainEvent):
    """Event published when a syllabus is deleted"""
    event_type: EventType = EventType.SYLLABUS_DELETED
    aggregate_type: str = "syllabus"


# Subject Event Schemas
class SubjectCreatedEvent(DomainEvent):
    """Event published when a subject is created"""
    event_type: EventType = EventType.SUBJECT_CREATED
    aggregate_type: str = "subject"


class SubjectUpdatedEvent(DomainEvent):
    """Event published when a subject is updated"""
    event_type: EventType = EventType.SUBJECT_UPDATED
    aggregate_type: str = "subject"


class SubjectDeletedEvent(DomainEvent):
    """Event published when a subject is deleted"""
    event_type: EventType = EventType.SUBJECT_DELETED
    aggregate_type: str = "subject"


# File Event Schemas
class FileUploadedEvent(DomainEvent):
    """Event published when a file is uploaded"""
    event_type: EventType = EventType.FILE_UPLOADED
    aggregate_type: str = "file"


class FileDeletedEvent(DomainEvent):
    """Event published when a file is deleted"""
    event_type: EventType = EventType.FILE_DELETED
    aggregate_type: str = "file"


# Event Publisher Interface
class EventPublisher:
    """Abstract base class for event publishers"""
    
    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event"""
        raise NotImplementedError
    
    async def publish_batch(self, events: list[DomainEvent]) -> None:
        """Publish multiple domain events"""
        raise NotImplementedError