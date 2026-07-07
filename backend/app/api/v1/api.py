# backend/app/api/v1/api.py
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, filaments, projects, orders, analytics, store

api_router = APIRouter()

# Include all the individual endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(filaments.router, prefix="/filaments", tags=["Filaments"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(store.router, prefix="/store", tags=["Bambu Store"])
