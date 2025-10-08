# repositories/user_repository.py
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from models.entities import User
from repositories.base import BaseRepository
from models.schemas import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):

    def __init__(self, session: Session):
        self.session = session

    def create(self, obj_in: UserCreate) -> User:
        # Nota: Asumimos que UserCreate tiene los campos necesarios para User
        user = User(**obj_in.dict())
        self.session.add(user)
        self.session.flush()  # Envía los cambios a la DB para obtener el ID, sin hacer commit
        self.session.refresh(user)
        return user

    def get(self, id: int) -> Optional[User]:
        return (
            self.session.query(User)
            .options(joinedload(User.roles))  # eager load roles
            .filter(User.id == id)
            .first()
        )

    def get_by_email(
        self, email: str
    ) -> Optional[User]:  # Añade este método si no lo tienes
        return (
            self.session.query(User)
            .options(joinedload(User.roles))  # eager load roles
            .filter(User.email == email)
            .first()
        )

    def get_all(self, skip=0, limit=100) -> List[User]:
        return (
            self.session.query(User)
            .options(joinedload(User.roles))  # eager load roles
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, db_obj: User, obj_in: UserUpdate) -> User:
        for k, v in obj_in.dict(exclude_unset=True).items():
            setattr(db_obj, k, v)
        self.session.flush()
        self.session.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> Optional[User]:
        obj = self.get(id)
        if obj:
            self.session.delete(obj)
            self.session.flush()
        return obj

    def asign_role_to_user(self, user: User, role) -> User:
        if role not in user.roles:
            user.roles.append(role)
            self.session.flush()
        return user
