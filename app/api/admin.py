from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from typing import List, Optional, UUID
from datetime import datetime, timedelta

from ..schemas.application import ApplicationResponse, ApplicationStatusUpdate
from ..schemas.user import UserResponse, UserPermissionUpdate
from ..schemas.admin import SystemSettings
from ..services.admin.admin_service import AdminService
from ..api.dependencies import get_current_admin_user, get_admin_service, get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.appointment_repository import AppointmentRepository
from app.models.appointment import AppointmentStatus
from app.models.user import User
from app.schemas.appointment import (
    AppointmentSlot,
    AppointmentSlotCreate,
    AppointmentAdminResponse,
    AppointmentStats,
    AppointmentsTimeRange
)
from app.services.appointment_service import AppointmentService

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

@router.post("/appointment-slots", response_model=AppointmentSlot, status_code=status.HTTP_201_CREATED)
async def create_appointment_slot(
    slot_data: AppointmentSlotCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new appointment slot (Admin only).
    """
    appointment_repository = AppointmentRepository(db)
    appointment_service = AppointmentService(appointment_repository)
    return await appointment_service.create_appointment_slot(slot_data)

@router.get("/appointment-slots", response_model=List[AppointmentSlot])
async def get_appointment_slots(
    location_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    available_only: bool = Query(False),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all appointment slots with optional filtering (Admin only).
    """
    appointment_repository = AppointmentRepository(db)
    appointment_service = AppointmentService(appointment_repository)
    return await appointment_service.get_all_slots(
        location_id=location_id,
        start_date=start_date,
        end_date=end_date,
        available_only=available_only
    )

@router.get("/appointment-slots/{slot_id}", response_model=AppointmentSlot)
async def get_appointment_slot(
    slot_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific appointment slot by ID (Admin only).
    """
    appointment_repository = AppointmentRepository(db)
    slot = await appointment_repository.get_slot_by_id(slot_id)
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment slot not found"
        )
    return slot

@router.put("/appointment-slots/{slot_id}", response_model=AppointmentSlot)
async def update_appointment_slot(
    slot_id: UUID,
    slot_data: AppointmentSlotCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an appointment slot (Admin only).
    """
    appointment_repository = AppointmentRepository(db)
    appointment_service = AppointmentService(appointment_repository)
    updated_slot = await appointment_service.update_appointment_slot(slot_id, slot_data)
    if not updated_slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment slot not found"
        )
    return updated_slot

@router.delete("/appointment-slots/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment_slot(
    slot_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an appointment slot if no active appointments (Admin only).
    """
    appointment_repository = AppointmentRepository(db)
    appointment_service = AppointmentService(appointment_repository)

    success = await appointment_service.delete_appointment_slot(slot_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment slot not found"
        )
    return None

@router.get("/appointments", response_model=List[AppointmentAdminResponse])
async def get_appointments(
    location_id: Optional[UUID] = None,
    status: Optional[AppointmentStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all appointments with optional filtering (Admin only).
    """
    appointment_repository = AppointmentRepository(db)
    appointment_service = AppointmentService(appointment_repository)
    return await appointment_service.get_all_appointments(
        location_id=location_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id
    )

@router.post("/appointments/stats", response_model=AppointmentStats)
async def get_appointment_stats(
    date_range: AppointmentsTimeRange,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get appointment statistics for a specific time range and optional location (Admin only).
    """
    appointment_repository = AppointmentRepository(db)

    # Get all appointments in the time range
    all_appointments = await appointment_repository.get_appointments(
        location_id=date_range.location_id,
        start_date=date_range.start_date,
        end_date=date_range.end_date
    )

    # Count appointments by status
    total = len(all_appointments)
    scheduled = sum(1 for a in all_appointments if a.status == AppointmentStatus.SCHEDULED)
    completed = sum(1 for a in all_appointments if a.status == AppointmentStatus.COMPLETED)
    cancelled = sum(1 for a in all_appointments if a.status == AppointmentStatus.CANCELLED)
    missed = sum(1 for a in all_appointments if a.status == AppointmentStatus.MISSED)

    return AppointmentStats(
        total=total,
        scheduled=scheduled,
        completed=completed,
        cancelled=cancelled,
        missed=missed
    )
