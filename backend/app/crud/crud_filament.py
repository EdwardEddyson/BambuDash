# backend/app/crud/crud_filament.py
from typing import Optional
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.crud.base import CRUDBase
from app.models.base_models import FilamentSpool, FilamentStatus
from app.schemas.filament import FilamentCreate, FilamentUpdate, FilamentEnrichment

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

    def get_or_create_from_mqtt(self, db: Session, *, mqtt_data: dict) -> FilamentSpool:
        """
        Finds a filament by its tray_id. If it exists, updates the weight.
        If not, creates a new DRAFT spool from the MQTT data.
        """
        tray_id = mqtt_data.get("tray_id")
        existing_spool = self.get_by_tray_id(db, tray_id=tray_id)

        if existing_spool:
            # Spool exists, just update the remaining weight
            update_data = {"remaining_weight_g": mqtt_data.get("weight", existing_spool.remaining_weight_g)}
            return self.update(db=db, db_obj=existing_spool, obj_in=update_data)
        else:
            # Spool does not exist, create a new one
            return self.create_from_mqtt(db=db, mqtt_data=mqtt_data)



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
