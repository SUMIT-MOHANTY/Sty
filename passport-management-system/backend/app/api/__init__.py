"""
API routes package for the passport management system.
"""
from fastapi import APIRouter

api_router = APIRouter()

# Import all routers
from .auth import router as auth_router
from .applications import router as applications_router
from .appointments import router as appointments_router
from .locations import router as locations_router
from .admin import admin_router
from .status import router as status_router

# Include all routers
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(applications_router, prefix="/applications", tags=["applications"])
api_router.include_router(appointments_router, prefix="/appointments", tags=["appointments"])
api_router.include_router(locations_router, prefix="/locations", tags=["locations"])
api_router.include_router(admin_router, prefix="/admin")
api_router.include_router(status_router, prefix="/status", tags=["status"])
