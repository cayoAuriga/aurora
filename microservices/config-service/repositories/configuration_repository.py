# repositories/configuration_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models.entities import Configuration
from models.schemas import ConfigurationCreate, ConfigurationUpdate
from repositories.base import BaseRepository

class ConfigurationRepository(BaseRepository[Configuration, ConfigurationCreate, ConfigurationUpdate]):
    
    def create(self, db: Session, obj_in: ConfigurationCreate) -> Configuration:
        """Crea una nueva configuración"""
        db_obj = Configuration(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Configuration]:
        """Obtiene una configuración por ID"""
        return db.query(Configuration).filter(Configuration.id == id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Configuration]:
        """Obtiene todas las configuraciones"""
        return db.query(Configuration)\
                .order_by(Configuration.created_at.desc())\
                .offset(skip)\
                .limit(limit)\
                .all()
    
    def get_by_key(self, db: Session, config_key: str, environment: str, service_name: str) -> Optional[Configuration]:
        """Obtiene una configuración por clave compuesta"""
        return db.query(Configuration).filter(
            and_(
                Configuration.config_key == config_key,
                Configuration.environment == environment,
                Configuration.service_name == service_name
            )
        ).first()
    
    def update(self, db: Session, db_obj: Configuration, obj_in: ConfigurationUpdate) -> Configuration:
        """Actualiza una configuración"""
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> Optional[Configuration]:
        """Elimina una configuración"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj