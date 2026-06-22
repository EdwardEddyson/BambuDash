# backend/app/main.py
from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title="BambuDash API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Include the main API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def startup_event():
    # Here you would start background tasks, e.g., the MQTT client
    # from app.services.mqtt_service import mqtt_client
    # mqtt_client.run()
    pass

@app.get("/", tags=["Root"])
def read_root():
    """A simple welcome message."""
    return {"message": "Welcome to the BambuDash API"}
