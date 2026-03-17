from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.applications import router as applications_router
from app.api.appointments import router as appointments_router
from app.api.admin import router as admin_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(applications_router, prefix="/applications", tags=["applications"])
api_router.include_router(appointments_router, prefix="/appointments", tags=["appointments"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
