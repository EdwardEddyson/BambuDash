# backend/app/api/v1/endpoints/projects.py
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.project import ProjectRead, ProjectCreate
from app.crud import crud_project

router = APIRouter()

@router.get("/", response_model=List[ProjectRead])
def get_all_projects(db: Session = Depends(get_db)):
    """
    Retrieve all projects.
    """
    return crud_project.get_multi(db)

@router.post("/", response_model=ProjectRead)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """
    Create a new project idea.
    """
    # Note: In a real app, you'd get the creator_id from the logged-in user (token)
    return crud_project.create_with_creator(db=db, obj_in=project, creator_id=1) # Placeholder creator_id
