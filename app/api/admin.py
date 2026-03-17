from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from typing import List, Optional
from ..schemas.application import ApplicationResponse, ApplicationStatusUpdate
from ..schemas.user import UserResponse, UserPermissionUpdate
from ..schemas.admin import SystemSettings
from ..services.admin.admin_service import AdminService
from ..api.dependencies import get_current_admin_user, get_admin_service

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/applications", response_model=List[ApplicationResponse])
async def get_all_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None),
    admin_service: AdminService = Depends(get_admin_service),
    _: dict = Depends(get_current_admin_user)
):
    """Get all passport applications with optional filtering by status"""
    return await admin_service.get_applications(skip=skip, limit=limit, status=status)

@router.patch("/applications/{application_id}", response_model=ApplicationResponse)
async def update_application_status(
    application_id: str = Path(...),
    status_update: ApplicationStatusUpdate = None,
    admin_service: AdminService = Depends(get_admin_service),
    _: dict = Depends(get_current_admin_user)
):
    """Update application status"""
    application = await admin_service.update_application_status(
        application_id=application_id,
        status_update=status_update
    )
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found"
        )
    return application

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    admin_service: AdminService = Depends(get_admin_service),
    _: dict = Depends(get_current_admin_user)
):
    """Get all system users"""
    return await admin_service.get_users(skip=skip, limit=limit)

@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user_permissions(
    user_id: str = Path(...),
    permission_update: UserPermissionUpdate = None,
    admin_service: AdminService = Depends(get_admin_service),
    _: dict = Depends(get_current_admin_user)
):
    """Update user permissions"""
    user = await admin_service.update_user_permissions(
        user_id=user_id,
        permission_update=permission_update
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user

@router.get("/settings", response_model=SystemSettings)
async def get_system_settings(
    admin_service: AdminService = Depends(get_admin_service),
    _: dict = Depends(get_current_admin_user)
):
    """Get system settings"""
    return await admin_service.get_settings()

@router.put("/settings", response_model=SystemSettings)
async def update_system_settings(
    settings: SystemSettings,
    admin_service: AdminService = Depends(get_admin_service),
    _: dict = Depends(get_current_admin_user)
):
    """Update system settings"""
    return await admin_service.update_settings(settings)
