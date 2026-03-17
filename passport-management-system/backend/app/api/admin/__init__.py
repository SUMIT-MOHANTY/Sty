from fastapi import APIRouter
from app.api.admin import applications, appointments, dashboard

# Create admin router
router = APIRouter(prefix="/admin", tags=["admin"])

# Include all admin endpoints
router.include_router(applications.router)
router.include_router(appointments.router)
router.include_router(dashboard.router)
