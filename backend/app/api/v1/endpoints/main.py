# backend/app/main.py
from fastapi import FastAPI
from sqlalchemy.orm import Session

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import engine
from app.models.base_models import SQLModel # Import the base model

# This is for development only, to create tables on startup.
# For production, you should use Alembic migrations.
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

app = FastAPI(
    title="BambuDash",
    description="A self-hosted management system for Bambu Lab 3D printers.",
    version="0.1.0"
)

@app.on_event("startup")
def on_startup():
    # Create database tables if they don't exist
    create_db_and_tables()

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Welcome to BambuDash API"}