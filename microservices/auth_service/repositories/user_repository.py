# repositories/user_repository.py
from typing import Optional, List
from sqlalchemy.orm import Session
from models.entities import User, Role, Permission

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def create(self, db: Session, obj_in: UserCreate) -> User:
        user = User(**obj_in.dict())
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get(self, db: Session, id: int) -> Optional[User]:
        return db.query(User).filter(User.id == id).first()

    def get_all(self, db: Session, skip=0, limit=100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    def update(self, db: Session, db_obj: User, obj_in: UserUpdate) -> User:
        for k, v in obj_in.dict(exclude_unset=True).items():
            setattr(db_obj, k, v)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> Optional[User]:
        obj = self.get(db, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj