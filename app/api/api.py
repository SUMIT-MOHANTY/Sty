from fastapi import APIRouter

from app.api.endpoints import users, auth, applications, status_history

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(applications.router)
api_router.include_router(status_history.router)
