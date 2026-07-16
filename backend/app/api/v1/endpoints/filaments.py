# backend/app/api/v1/endpoints/filaments.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.filament import FilamentRead, FilamentEnrichment, FilamentAssignAMS

from app.crud import crud_filament
from app.models.base_models import FilamentSpool

router = APIRouter()

@router.get("/", response_model=List[FilamentRead])
def get_all_filaments(db: Session = Depends(get_db)):
    """
    Retrieve all filament spools.
    """
    return crud_filament.get_multi(db)

@router.put("/{filament_id}/enrich", response_model=FilamentRead)
def enrich_filament_data(filament_id: int, enrichment_data: FilamentEnrichment, db: Session = Depends(get_db)):
    """
    Enrich a 'DRAFT' filament spool with price and owner information.
    """
    db_filament = crud_filament.get(db, id=filament_id)
    if not db_filament:
        raise HTTPException(status_code=404, detail="Filament not found")

    # Here you would call a service function to apply the logic
    # For now, we call crud directly
    updated_filament = crud_filament.enrich(db=db, db_obj=db_filament, obj_in=enrichment_data)
    return updated_filament


@router.post("/{filament_id}/assign-ams", response_model=FilamentRead)
def assign_filament_to_ams(filament_id: int, assign_data: FilamentAssignAMS, db: Session = Depends(get_db)):
    """Assign an existing filament spool to a printer's AMS slot."""
    db_filament = crud_filament.get(db, id=filament_id)
    if not db_filament:
        raise HTTPException(status_code=404, detail="Filament not found")
    return crud_filament.assign_ams(db=db, db_obj=db_filament, bambu_tray_id=assign_data.bambu_tray_id)

@router.post("/{filament_id}/remove-ams", response_model=FilamentRead)
def remove_filament_from_ams(filament_id: int, db: Session = Depends(get_db)):
    """Remove a spool from its AMS tray (putting it back to standby)."""
    db_filament = crud_filament.get(db, id=filament_id)
    if not db_filament:
        raise HTTPException(status_code=404, detail="Filament not found")
    return crud_filament.remove_ams(db=db, db_obj=db_filament)
