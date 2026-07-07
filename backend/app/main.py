
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from contextlib import asynccontextmanager

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import engine
# Import all models here so that SQLModel can discover them
from app.models import base_models
from app.services.mqtt_service import mqtt_client


def create_db_and_tables():
    """
    Creates all database tables defined by SQLModel models.
    This is useful for initial setup and development environments.
    In a production environment, you would typically use a migration
    tool like Alembic.
    """
    print("Creating database and tables...")
    SQLModel.metadata.create_all(engine)
    print("Database and tables created successfully.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    create_db_and_tables()
    try:
        mqtt_client.run()
    except Exception as e:
        print(f"Failed to start MQTT client: {e}")
    yield
    # Shutdown actions
    try:
        mqtt_client.stop()
    except Exception as e:
        print(f"Failed to stop MQTT client: {e}")


app = FastAPI(
    title="BambuDash API",
    description="Backend for the BambuDash 3D Print Management System.",
    version="0.1.0",
    lifespan=lifespan,
)

# Set up CORS (Cross-Origin Resource Sharing)
# This is necessary to allow the frontend (running on a different port/domain)
# to communicate with the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for simplicity in development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)



# Include the main API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Health Check"])
def read_root():
    """
    Root endpoint for basic health checks.
    """
    return {"status": "ok", "message": "Welcome to the BambuDash API!"}
