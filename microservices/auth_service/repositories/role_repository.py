# repositories/role_repository.py
from models.entities import Role, Permission
from sqlalchemy.orm import Session
from typing import Optional, List

class RoleRepository(BaseRepository[Role, RoleCreate, RoleUpdate]):
    """Repositorio de roles"""

    def create(self, db: Session, obj_in: RoleCreate) -> Role:
        role = Role(**obj_in.dict())
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    def get(self, db: Session, role_id: int) -> Optional[Role]:
        return db.query(Role).filter(Role.id == role_id).first()

    def get_all(self, db: Session) -> List[Role]:
        return db.query(Role).all()

    def assign_permission(self, db: Session, role: Role, permission: Permission):
        role.permissions.append(permission)
        db.commit()
        db.refresh(role)
        return role