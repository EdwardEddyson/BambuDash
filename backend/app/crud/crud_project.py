# backend/app/crud/crud_project.py
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.base_models import PrintProject
from app.schemas.project import ProjectCreate, ProjectUpdate # Define ProjectUpdate in schemas

class CRUDProject(CRUDBase[PrintProject, ProjectCreate, ProjectUpdate]):
    def create_with_creator(self, db: Session, *, obj_in: ProjectCreate, creator_id: int) -> PrintProject:
        db_obj = PrintProject(
            **obj_in.dict(),
            creator_id=creator_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

project = CRUDProject(PrintProject)
