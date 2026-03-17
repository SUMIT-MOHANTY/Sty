from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user
from app.db.repositories.appointment_repository import AppointmentRepository
from app.models.appointment import AppointmentStatus
from app.models.user import User
from app.schemas.appointment import (
    AppointmentSlot,
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate
)
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.get("/available-slots", response_model=List[AppointmentSlot])
async def get_available_slots(
    location_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get available appointment slots for booking.
    """
    if not start_date:
        start_date = datetime.now()
    if not end_date:
        end_date = start_date + timedelta(days=30)

    appointment_repository = AppointmentRepository(db)
    appointment_service = AppointmentService(appointment_repository)
    return await appointment_service.get_all_slots(
        location_id=location_id,
        start_date=start_date,
        end_date=end_date,
        available_only=True
    )

@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def book_appointment(
    appointment_data: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Book a new appointment.
    """
    # Implementation would normally validate:
    # 1. Slot is available
    # 2. Application exists and belongs to user
    # 3. User doesn't already have an active appointment for this application

    # This is simplified for now
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Booking functionality not fully implemented"
    )

@router.get("/my-appointments", response_model=List[AppointmentResponse])
async def get_user_appointments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all appointments for the current user.
    """
    appointment_repository = AppointmentRepository(db)
    appointment_service = AppointmentService(appointment_repository)

    # Use the admin method but filter by current user
    appointments = await appointment_service.get_all_appointments(
        user_id=current_user.id
    )

    # Convert to regular appointment responses
    return appointments

@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: UUID = Path(...),
    update_data: AppointmentUpdate = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an appointment (e.g., cancel).
    Users can only cancel their own appointments.
    """
    # Implementation would normally:
    # 1. Check that the appointment belongs to the user
    # 2. Check that the appointment is not in the past
    # 3. Update the appointment status

    # This is simplified for now
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Update functionality not fully implemented"
    )
