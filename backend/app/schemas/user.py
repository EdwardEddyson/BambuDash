
from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel

from app.models.base_models import UserRole

# ---------------------------------
# User Schemas
# ---------------------------------

# Base properties for a user, shared by other schemas
class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)

# Properties to receive via API on user creation
class UserCreate(UserBase):
    password: str
    role: Optional[UserRole] = UserRole.USER

# Properties to receive via API on user update
# All fields are optional for partial updates
class UserUpdate(SQLModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None

# Properties to return to client
# This model is used for reading user data from the API
class UserRead(UserBase):
    id: int
    role: UserRole
    created_at: datetime

# Properties stored in DB
# This is not a schema, but often kept with schemas.
# However, our main model is in base_models.py, which is correct.

