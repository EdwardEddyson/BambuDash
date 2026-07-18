# backend/app/api/v1/endpoints/projects.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.project import ProjectRead, ProjectCreate, ProjectFeasibility, ProjectFilamentRequirementCreate, ProjectFilamentRequirementRead
from app.crud import crud_project, crud_filament
from app.api.deps import get_current_user
from app.models.base_models import User, ProjectFilamentRequirement

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

from app.schemas.project import ProjectUpdate

@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing project (e.g. status change).
    """
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found.")

    return crud_project.update(db=db, db_obj=project, obj_in=project_update)

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

    required_weight = sum(req.estimated_consumption_g for req in project.requirements) if project.requirements else 0
    is_feasible = filament_spool.remaining_weight_g >= required_weight

    return ProjectFeasibility(
        is_feasible=is_feasible,
        project_id=project_id,
        required_weight_g=required_weight,
        filament_spool_id=filament_spool_id,
        available_weight_g=filament_spool.remaining_weight_g,
    )

@router.post("/{project_id}/requirements", response_model=ProjectFilamentRequirementRead)
def add_project_requirement(
    project_id: int,
    requirement: ProjectFilamentRequirementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Add a filament requirement to a project.
    """
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found.")

    existing_req = db.query(ProjectFilamentRequirement).filter(
        ProjectFilamentRequirement.project_id == project_id,
        ProjectFilamentRequirement.material_type == requirement.material_type,
        ProjectFilamentRequirement.color_hex == requirement.color_hex
    ).first()

    if existing_req:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Requirement for this material and color already exists.")

    db_req = ProjectFilamentRequirement(
        project_id=project_id,
        material_type=requirement.material_type,
        color_hex=requirement.color_hex,
        estimated_consumption_g=requirement.estimated_consumption_g
    )
    db.add(db_req)
    db.commit()
    db.refresh(db_req)
    return db_req

@router.delete("/{project_id}/requirements")
def remove_project_requirement(
    project_id: int,
    material_type: str = Query(...),
    color_hex: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Remove a filament requirement from a project.
    """
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found.")

    db_req = db.query(ProjectFilamentRequirement).filter(
        ProjectFilamentRequirement.project_id == project_id,
        ProjectFilamentRequirement.material_type == material_type,
        ProjectFilamentRequirement.color_hex == color_hex
    ).first()

    if not db_req:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Requirement not found.")

    db.delete(db_req)
    db.commit()
    return {"ok": True}
