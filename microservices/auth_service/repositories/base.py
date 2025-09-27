from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional
from sqlalchemy.orm import Session

T = TypeVar('T')
CreateSchemaType = TypeVar('CreateSchemaType')
UpdateSchemaType = TypeVar('UpdateSchemaType')


class BaseRepository(ABC, Generic[T, CreateSchemaType, UpdateSchemaType]):
    """Base interface for auth service repositories"""

    @abstractmethod
    def create(self, db: Session, obj_in: CreateSchemaType) -> T:
        pass

    @abstractmethod
    def get(self, db: Session, id: int) -> Optional[T]:
        pass

    @abstractmethod
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[T]:
        pass

    @abstractmethod
    def update(self, db: Session, db_obj: T, obj_in: UpdateSchemaType) -> T:
        pass

    @abstractmethod
    def delete(self, db: Session, id: int) -> Optional[T]:
        pass
