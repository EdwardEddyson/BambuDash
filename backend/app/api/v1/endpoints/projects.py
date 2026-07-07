# backend/app/api/v1/endpoints/projects.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.project import ProjectRead, ProjectCreate, ProjectFeasibility
from app.crud import crud_project, crud_filament
from app.api.deps import get_current_user
from app.models.base_models import User

router = APIRouter()

@router.get("/", response_model=List[ProjectRead])
def get_all_projects(db: Session = Depends(get_db)):
    """
    Retrieve all projects.
    """
    return crud_project.get_multi(db)

@router.post("/", response_model=ProjectRead)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new project idea.
    """
    return crud_project.create_with_creator(db=db, obj_in=project, creator_id=current_user.id)

@router.get("/{project_id}/feasibility", response_model=ProjectFeasibility)
def check_project_feasibility(
    project_id: int,
    filament_spool_id: int = Query(..., description="The ID of the filament spool to check against."),
    db: Session = Depends(get_db)
):
    """
    Checks if a filament spool has enough material for a specific project.
    """
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found.")

    filament_spool = crud_filament.get(db, id=filament_spool_id)
    if not filament_spool:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Filament spool not found.")

    required_weight = project.slicer_filament_weight_g or 0
    is_feasible = filament_spool.remaining_weight_g >= required_weight

    return ProjectFeasibility(
        is_feasible=is_feasible,
        project_id=project_id,
        required_weight_g=required_weight,
        filament_spool_id=filament_spool_id,
        available_weight_g=filament_spool.remaining_weight_g,
    )
