import os
import sys

sys.path.insert(0, os.path.abspath('backend'))

from app.schemas.filament import FilamentAssignAMS
from app.crud.crud_filament import filament
print('Successfully imported and parsed all modified files.')
