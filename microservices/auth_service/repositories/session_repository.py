# repositories/session_repository.py
from typing import Optional, List
from datetime import datetime
from pymongo.collection import Collection
from models.entities import SessionModel
from pydantic import parse_obj_as
from repositories.base import BaseRepository
from models.schemas import SessionCreate, SessionRead

class SessionRepository(BaseRepository[SessionModel, SessionModel, SessionCreate]):
    """Repositorio para manejar sesiones en MongoDB"""

    def __init__(self, collection: Collection):
        self.collection = collection

    def create(self, session: SessionCreate) -> SessionRead:
        data = session.dict()
        data["created_at"] = datetime.utcnow()
        self.collection.insert_one(data)
        return SessionRead(**data)

    def get_by_session_id(self, session_id: str) -> Optional[SessionRead]:
        doc = self.collection.find_one({"session_id": session_id})
        if doc:
            return SessionRead(**doc)
        return None

    def delete(self, session_id: str) -> bool:
        result = self.collection.delete_one({"session_id": session_id})
        return result.deleted_count > 0

    def get_by_user_id(self, user_id: int) -> List[SessionModel]:
        """Obtiene todas las sesiones activas de un usuario"""
        docs = self.collection.find({"user_id": user_id})
        return parse_obj_as(List[SessionModel], list(docs))

    def invalidate_expired(self) -> int:
        """Elimina todas las sesiones que hayan expirado"""
        now = datetime.utcnow()
        result = self.collection.delete_many({"expires_at": {"$lte": now}})
        return result.deleted_count

    def update_tokens(self, session_id: str, access_token: str, refresh_token: str) -> Optional[SessionModel]:
        """Actualiza los tokens de una sesión existente"""
        update = {
            "$set": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "updated_at": datetime.utcnow()
            }
        }
        doc = self.collection.find_one_and_update({"session_id": session_id}, update, return_document=True)
        if doc:
            return SessionModel.model_validate(doc)
        return None
