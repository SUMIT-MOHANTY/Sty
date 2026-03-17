"""
Admin API routes package for administrative operations.
"""
from fastapi import APIRouter

admin_router = APIRouter(prefix="/admin", tags=["admin"])

# Import and include all admin-related routers
from .applications import router as applications_router
from .appointments import router as appointments_router
from .dashboard import router as dashboard_router

admin_router.include_router(applications_router)
admin_router.include_router(appointments_router)
admin_router.include_router(dashboard_router)
