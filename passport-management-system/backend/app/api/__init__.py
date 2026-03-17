from fastapi import APIRouter
from .auth import router as auth_router

api_router = APIRouter()

# Include all API routes
api_router.include_router(auth_router, prefix="/auth")
# Add other routers as needed: applications, appointments, etc.
