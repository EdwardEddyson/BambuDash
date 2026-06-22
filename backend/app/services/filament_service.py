# backend/app/services/filament_service.py
from sqlalchemy.orm import Session
from app.crud import crud_filament
from app.models.base_models import FilamentSpool

def get_total_available_weight(db: Session, material_type: str, color_hex: str) -> float:
    """
    Calculates the total weight of available filament for a specific type and color.
    This is used by the project_service for the "live check".
    """
    # This requires a custom CRUD function to be written
    # e.g., crud_filament.get_sum_of_available_weight_by_type(...)
    print(f"Checking availability for {material_type} in {color_hex}...")
    return 500.0 # Placeholder value
