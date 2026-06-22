# backend/app/services/project_service.py
from sqlalchemy.orm import Session
from app.models.base_models import PrintProject
from app.services import filament_service

def check_project_feasibility(db: Session, project: PrintProject) -> bool:
    """
    The "Live-Realisierungs-Check".
    Checks if there is enough filament in stock for a planned project.
    """
    for requirement in project.filament_requirements:
        available_weight = filament_service.get_total_available_weight(
            db,
            material_type=requirement.material_type,
            color_hex=requirement.color_hex
        )
        if available_weight < requirement.estimated_consumption_g:
            return False # Not enough filament for this requirement
    return True # All requirements can be met
