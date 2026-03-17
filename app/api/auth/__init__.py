from fastapi import APIRouter
from .routes import router as auth_router

# Create a router for the auth module
router = APIRouter()

# Include the routes from the routes module
router.include_router(auth_router, prefix="/auth", tags=["auth"])
