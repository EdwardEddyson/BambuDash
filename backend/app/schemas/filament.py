# backend/app/schemas/filament.py
from typing import Optional
from sqlmodel import SQLModel
from app.models.base_models import FilamentStatus, SpoolType

# Shared properties
class FilamentBase(SQLModel):
    material_type: str
    color_hex: str
    remaining_weight_g: float
    status: FilamentStatus

# Properties to return to client
class FilamentRead(FilamentBase):
    id: int
    bambu_tray_id: Optional[str]
    price: Optional[float]
    spool_type: SpoolType
    owner_id: Optional[int]

# Properties for the user to provide during enrichment
class FilamentEnrichment(SQLModel):
    price: float
    owner_id: int
    spool_type: SpoolType = SpoolType.SPOOL
