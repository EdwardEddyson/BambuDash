# backend/app/db/base.py
# This file is used to make all models available for database tools like Alembic.
# By importing them here, we ensure they are registered with SQLModel's metadata.

from app.models.base_models import (
    User,
    Printer,
    FilamentSpool,
    PrintProject,
    PrintJob,
    Order,
    OrderItem,
    OrderItemSplit,
    ProjectFilamentRequirement
)
