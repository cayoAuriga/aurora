from typing import Optional
from sqlalchemy.orm import Session

from models.entities import AuthProvider
from models.schemas import AuthProviderCreate # Usamos nuestro nuevo schema
from repositories.base import BaseRepository

class AuthProviderRepository(BaseRepository[AuthProvider, AuthProviderCreate, None]):
    """
    Repositorio para manejar proveedores de autenticación.
    Sigue el patrón Unit of Work.
    """
    def __init__(self, session: Session):
        self.session = session

    def create(self, obj_in: AuthProviderCreate) -> AuthProvider:
        """Crea un nuevo registro de proveedor de autenticación."""
        db_obj = AuthProvider(**obj_in.model_dump())
        self.session.add(db_obj)
        self.session.flush()
        self.session.refresh(db_obj)
        return db_obj

    def get(self, id: int) -> Optional[AuthProvider]:
        """Obtiene un proveedor por su ID primario."""
        return self.session.query(AuthProvider).filter(AuthProvider.id == id).first()

    def get_by_provider_user_id(
        self, provider: str, provider_user_id: str
    ) -> Optional[AuthProvider]:
        """
        Busca un proveedor por la combinación única de
        nombre del proveedor y el ID del usuario en ese proveedor.
        Este es el método de búsqueda principal.
        """
        return (
            self.session.query(AuthProvider)
            .filter(
                AuthProvider.provider == provider,
                AuthProvider.provider_user_id == provider_user_id,
            )
            .first()
        )
    def delete(self, id: int) -> Optional[AuthProvider]:
        """Elimina un proveedor por su ID primario."""
        auth_provider = self.get(id)
        if auth_provider:
            self.session.delete(auth_provider)
            self.session.flush()
        return auth_provider
    def get_all(self) -> list[AuthProvider]:
        """Obtiene todos los proveedores de autenticación."""
        return self.session.query(AuthProvider).all()
    def update(self, obj: AuthProvider) -> AuthProvider:
        """Actualiza un proveedor de autenticación existente."""
        self.session.merge(obj)
        self.session.flush()
        self.session.refresh(obj)
        return obj