# repositories/permission_repository.py
from models.entities import Permission
from sqlalchemy.orm import Session
from typing import Optional, List

class PermissionRepository(BaseRepository[Permission, PermissionCreate, PermissionUpdate]):
    """Repositorio de permisos"""

    def create(self, db: Session, obj_in: PermissionCreate) -> Permission:
        perm = Permission(**obj_in.dict())
        db.add(perm)
        db.commit()
        db.refresh(perm)
        return perm

    def get(self, db: Session, perm_id: int) -> Optional[Permission]:
        return db.query(Permission).filter(Permission.id == perm_id).first()

    def get_all(self, db: Session) -> List[Permission]:
        return db.query(Permission).all()
