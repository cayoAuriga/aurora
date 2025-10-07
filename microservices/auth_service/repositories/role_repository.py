# repositories/role_repository.py
from models.entities import Role, Permission
from sqlalchemy.orm import Session, joinedload 
from typing import Optional, List
from models.schemas import RoleCreate, RoleUpdate
from repositories.base import BaseRepository
class RoleRepository(BaseRepository[Role, RoleCreate, RoleUpdate]):
    """Repositorio de roles"""
    def __init__(self, session: Session):
        self.session = session

    def create(self, role: RoleCreate) -> Role:
        role = Role(**role.dict())
        self.session.add(role)
        self.session.flush()
        self.session.refresh(role)
        return role

    def get(self, role_id: int) -> Optional[Role]:
        return self.session.query(Role).filter(Role.id == role_id).first()

    def get_by_name(self, name: str) -> Optional[Role]:
        return self.session.query(Role).filter(Role.name == name).first()
    
    def assig_permission_to_role(self, role: Role, permission: Permission) -> Role:
        if permission not in role.permissions:
            role.permissions.append(permission)
            self.session.flush()
        return role
    
    def revoke_permission_from_role(self, role: Role, permission: Permission) -> Role:
        if permission in role.permissions:
            role.permissions.remove(permission)
            self.session.flush()
        return role
    
    def get_all(self) -> List[Role]:
        """Obtiene todos los roles, cargando sus permisos de forma anticipada."""
        return self.session.query(Role).options(joinedload(Role.permissions)).all()
    
    def update(self, role: Role, permissions: List[Permission]) -> Role:
        role.permissions = permissions
        self.session.flush()
        return role
    
    def delete(self, role_id: int) -> Optional[Role]:
        role = self.get(role_id)
        if role:
            self.session.delete(role)
            self.session.flush()
        return role