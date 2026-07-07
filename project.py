# backend/app/schemas/project.py
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

# ---------------------------------
# Project Schemas
# ---------------------------------

# Base properties for a project
class ProjectBase(SQLModel):
    name: str
    description: Optional[str] = None
    slicer_filament_weight_g: Optional[float] = Field(
        default=None, description="Estimated filament weight in grams from the slicer."
    )

# Properties to receive via API on creation
class ProjectCreate(ProjectBase):
    pass

# Properties to receive via API on update
class ProjectUpdate(ProjectBase):
    name: Optional[str] = None # All fields optional for PATCH

# Properties to return to client
class ProjectRead(ProjectBase):
    id: int
    creator_id: int
    created_at: datetime

# Schema for the feasibility check response
class ProjectFeasibility(SQLModel):
    is_feasible: bool
    project_id: int
    required_weight_g: float
    filament_spool_id: int
    available_weight_g: float
