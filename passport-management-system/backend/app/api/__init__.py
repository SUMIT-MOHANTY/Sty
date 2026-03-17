from fastapi import APIRouter
from .auth import router as auth_router
from .applications import router as applications_router
from .appointments import router as appointments_router
from .locations import router as locations_router
from .admin import applications as admin_applications_router
from .admin import appointments as admin_appointments_router
from .admin import dashboard as admin_dashboard_router

# Main API router
api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router)
api_router.include_router(applications_router)
api_router.include_router(appointments_router)
api_router.include_router(locations_router)

# Include admin routers
api_router.include_router(admin_applications_router.router, prefix="/admin")
api_router.include_router(admin_appointments_router.router, prefix="/admin")
api_router.include_router(admin_dashboard_router.router, prefix="/admin")
