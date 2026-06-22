# backend/app/crud/crud_filament.py
from typing import Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.base_models import FilamentSpool, FilamentStatus
from app.schemas.filament import FilamentEnrichment # Assuming a create schema exists

# Dummy schemas for CRUDBase generic
from pydantic import BaseModel
class FilamentCreate(BaseModel):
    pass
class FilamentUpdate(BaseModel):
    pass

class CRUDFilament(CRUDBase[FilamentSpool, FilamentCreate, FilamentUpdate]):
    def get_by_tray_id(self, db: Session, *, tray_id: str) -> Optional[FilamentSpool]:
        """Finds a filament by its AMS tray UID."""
        return db.query(FilamentSpool).filter(FilamentSpool.bambu_tray_id == tray_id).first()

    def create_from_mqtt(self, db: Session, *, mqtt_data: dict) -> FilamentSpool:
        """Creates a new DRAFT filament spool from MQTT data."""
        # This is a simplified example. You'd parse mqtt_data properly.
        new_spool = FilamentSpool(
            bambu_tray_id=mqtt_data.get("tray_id"),
            material_type=mqtt_data.get("material", "unknown"),
            color_hex=mqtt_data.get("color", "#FFFFFF"),
            remaining_weight_g=mqtt_data.get("weight", 0),
            status=FilamentStatus.DRAFT,
        )
        db.add(new_spool)
        db.commit()
        db.refresh(new_spool)
        return new_spool
        
    def enrich(self, db: Session, *, db_obj: FilamentSpool, obj_in: FilamentEnrichment) -> FilamentSpool:
        """Updates a DRAFT spool with user-provided data."""
        db_obj.price = obj_in.price
        db_obj.owner_id = obj_in.owner_id
        db_obj.spool_type = obj_in.spool_type
        db_obj.status = FilamentStatus.AVAILABLE # Change status from DRAFT to AVAILABLE
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


filament = CRUDFilament(FilamentSpool)
