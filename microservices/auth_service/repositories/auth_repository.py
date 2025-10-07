# repositories/auth_provider_repository.py
from typing import Optional
from sqlalchemy.orm import Session
from models.entities import AuthProvider
from models.schemas import AuthProviderCreate, AuthProviderUpdate
from repostories.base import BaseRepository


class AuthProviderRepository(BaseRepository[AuthProvider, AuthProviderCreate, AuthProviderUpdate]):
    """Repositorio para manejar proveedores de autenticación"""

    def create(self, db: Session, obj_in: AuthProviderCreate) -> AuthProvider:
        db_obj = AuthProvider(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: int) -> Optional[AuthProvider]:
        return db.query(AuthProvider).filter(AuthProvider.id == id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(AuthProvider).offset(skip).limit(limit).all()

    def get_by_provider_user_id(
        self, db: Session, provider: str, provider_user_id: str
    ) -> Optional[AuthProvider]:
        return (
            db.query(AuthProvider)
            .filter(
                AuthProvider.provider == provider,
                AuthProvider.provider_user_id == provider_user_id,
            )
            .first()
        )

    def update(self, db: Session, db_obj: AuthProvider, obj_in: AuthProviderUpdate) -> AuthProvider:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> Optional[AuthProvider]:
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj
