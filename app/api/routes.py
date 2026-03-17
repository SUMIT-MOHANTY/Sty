from fastapi import APIRouter

from app.api import auth, applications, appointments, admin

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
