# backend/app/crud/crud_user.py
from typing import Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.base_models import User
from app.schemas.user import UserCreate, UserUpdate # UserUpdate would be defined in schemas
from app.core.security import get_password_hash, verify_password

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            role=obj_in.role,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[User]:
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

user = CRUDUser(User)

# Dummy UserUpdate for CRUDBase generic
from pydantic import BaseModel
class UserUpdate(BaseModel):
    pass
