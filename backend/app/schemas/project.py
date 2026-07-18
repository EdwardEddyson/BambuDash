from typing import Optional, List
import re
from pydantic import validator
from sqlmodel import SQLModel, Field
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

class ProjectFilamentRequirementCreate(SQLModel):
    material_type: str = Field(..., min_length=1)
    color_hex: str = Field(..., description="HTML hex color code, e.g., '#FFFFFF'")
    estimated_consumption_g: float = Field(..., gt=0, description="Must be positive")

    @validator('color_hex')
    def validate_color_hex(cls, v):
        if not re.match(r"^#[0-9a-fA-F]{6}$", v):
            raise ValueError('color_hex must be a valid hex color code like #FFFFFF')
        return v

class ProjectFilamentRequirementRead(ProjectFilamentRequirementCreate):
    project_id: int

# Properties to return to client
class ProjectRead(ProjectBase):
    id: int
    creator_id: int
    filament_requirements: List[ProjectFilamentRequirementRead] = []

# Schema for the feasibility check response
class ProjectFeasibility(SQLModel):
    is_feasible: bool
    project_id: int
    required_weight_g: float
    filament_spool_id: int
    available_weight_g: float
