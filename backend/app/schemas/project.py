# backend/app/schemas/project.py
from typing import Optional, List
from sqlmodel import SQLModel
from app.models.base_models import ProjectStatus

# Shared properties
class ProjectBase(SQLModel):
    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.IDEA
    image_stl_url: Optional[str] = None

# Properties to receive on creation
class ProjectCreate(ProjectBase):
    # creator_id will be derived from the logged-in user's token
    pass

# Properties to receive via API on project update
# All fields are optional for partial updates
class ProjectUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    image_stl_url: Optional[str] = None

# Properties to return to client
class ProjectRead(ProjectBase):
    id: int
    creator_id: int

# You might also want schemas for filament requirements
class ProjectFilamentRequirement(SQLModel):
    material_type: str
    color_hex: str
    estimated_consumption_g: float
