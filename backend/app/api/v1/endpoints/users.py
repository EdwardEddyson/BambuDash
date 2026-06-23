# backend/app/api/v1/endpoints/users.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserRead, UserCreate

router = APIRouter()

@router.post("/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Creates a new user.
    """
    db_user = crud_user.get_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud_user.create(db=db, user=user)

@router.get("/", response_model=List[UserRead])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve users.
    """
    users = crud_user.get_multi(db, skip=skip, limit=limit)
    return users
