# backend/app/api/v1/endpoints/filaments.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.filament import FilamentRead, FilamentCreate, FilamentEnrichment, FilamentUpdate
from app.crud import crud_filament

router = APIRouter()

@router.get("/", response_model=List[FilamentRead])
def get_all_filaments(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Retrieve all filament spools.
    """
    return crud_filament.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=FilamentRead, status_code=status.HTTP_201_CREATED)
def create_filament(filament: FilamentCreate, db: Session = Depends(get_db)):
    """
    Create a new filament spool manually.
    """
    # In a real app, owner_id might come from the logged-in user
    return crud_filament.create(db=db, obj_in=filament)

@router.patch("/{filament_id}", response_model=FilamentRead)
def enrich_filament(filament_id: int, filament_in: FilamentEnrichment, db: Session = Depends(get_db)):
    """
    Enrich a DRAFT filament spool with details like price and owner to make it AVAILABLE.
    """
    db_filament = crud_filament.get(db, id=filament_id)
    if not db_filament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filament spool not found.",
        )

    enriched_filament = crud_filament.enrich(db=db, db_obj=db_filament, obj_in=filament_in)
    return enriched_filament
