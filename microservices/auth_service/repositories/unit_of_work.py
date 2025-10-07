# repositories/unit_of_work.py

from __future__ import annotations
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

# Importa la factoría de sesiones de tu archivo de base de datos
from database import SessionLocal 

# Importa las clases de tus repositorios
from repositories.user_repository import UserRepository
from repositories.role_repository import RoleRepository
from repositories.permission_repository import PermissionRepository
from repositories.auth_provider_repository import AuthProviderRepository

class AbstractUnitOfWork(ABC):
    """Interfaz abstracta para el Unit of Work."""
    users: UserRepository
    roles: RoleRepository
    permissions: PermissionRepository
    auth_providers: AuthProviderRepository

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        # Si hay una excepción, realiza un rollback
        if exc_type:
            self.rollback()

    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError

class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """Implementación del Unit of Work para SQLAlchemy."""
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    def __enter__(self):
        self.session: Session = self.session_factory()
        
        # Instanciamos los repositorios con la sesión creada
        self.users = UserRepository(self.session)
        self.roles = RoleRepository(self.session)
        self.permissions = PermissionRepository(self.session)
        self.auth_providers = AuthProviderRepository(self.session)
        
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, traceback):
        super().__exit__(exc_type, exc_val, traceback)
        # Si no hubo excepción, hacemos commit
        if not exc_type:
            self.commit()
        
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
