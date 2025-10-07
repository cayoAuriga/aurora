# repositories/permission_repository.py
from models.entities import Permission
from sqlalchemy.orm import Session
from typing import Optional, List
from models.schemas import PermissionCreate, PermissionUpdate
from repositories.base import BaseRepository
class PermissionRepository(BaseRepository[Permission, PermissionCreate, PermissionUpdate]):
    """Repositorio de permisos"""
    def __init__(self, session: Session):
        self.session = session

        
    def create(self, obj_in: PermissionCreate) -> Permission:        
        perm = Permission(**obj_in.dict())
        self.session.add(perm)
        self.session.flush()
        self.session.refresh(perm)
        return perm

    def get(self, perm_id: int) -> Optional[Permission]:
        return self.session.query(Permission).filter(Permission.id == perm_id).first()

    def update(self, obj: Permission) -> Permission:
        self.session.merge(obj)
        self.session.flush()
        self.session.refresh(obj)
        return obj

    def get_all(self) -> List[Permission]:
        return self.session.query(Permission).all()
    
    def get_by_name(self, name: str) -> Optional[Permission]:
        return self.session.query(Permission).filter(Permission.name == name).first()
    
    def get_many_by_names(self, names: List[str]) -> List[Permission]:
        return self.session.query(Permission).filter(Permission.name.in_(names)).all()
    
    def delete(self, perm_id: int) -> Optional[Permission]:
        perm = self.get(perm_id)
        if perm:
            self.session.delete(perm)
            self.session.flush()
        return perm
