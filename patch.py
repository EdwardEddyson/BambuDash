import sys

path = 'backend/app/crud/crud_filament.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

new_code = '''
    def assign_ams(self, db: Session, *, db_obj: FilamentSpool, bambu_tray_id: str) -> FilamentSpool:
        """Assign a spool to an AMS tray, evicting any other spool in that tray."""
        existing = self.get_by_tray_id(db, tray_id=bambu_tray_id)
        if existing and existing.id != db_obj.id:
            existing.bambu_tray_id = None
            db.add(existing)
        db_obj.bambu_tray_id = bambu_tray_id
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove_ams(self, db: Session, *, db_obj: FilamentSpool) -> FilamentSpool:
        """Remove a spool from its AMS tray."""
        db_obj.bambu_tray_id = None
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

filament = CRUDFilament(FilamentSpool)
'''

content = content.replace('filament = CRUDFilament(FilamentSpool)', new_code)
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

path_api = 'backend/app/api/v1/endpoints/filaments.py'
with open(path_api, 'r', encoding='utf-8') as f:
    content_api = f.read()

api_imports_patch = "from app.schemas.filament import FilamentRead, FilamentEnrichment, FilamentAssignAMS\n"
content_api = content_api.replace("from app.schemas.filament import FilamentRead, FilamentEnrichment", api_imports_patch)

api_endpoints = '''
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
'''
content_api += "\n" + api_endpoints
with open(path_api, 'w', encoding='utf-8') as f:
    f.write(content_api)
