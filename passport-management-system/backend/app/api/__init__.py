from fastapi import APIRouter
from app.api import auth, applications, appointments, locations
from app.api.admin import applications as admin_applications
from app.api.admin import appointments as admin_appointments
from app.api.admin import dashboard as admin_dashboard

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(applications.router)
api_router.include_router(appointments.router)
api_router.include_router(locations.router)

# Admin routes
api_router.include_router(admin_applications.router)
api_router.include_router(admin_appointments.router)
api_router.include_router(admin_dashboard.router)
