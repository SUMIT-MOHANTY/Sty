from typing import List, Optional, UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, Path
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.appointment import AppointmentStatus
from app.models.user import User
from app.schemas.appointment import (
    AppointmentSlot,
    AppointmentCreate, 
    AppointmentUpdate, 
    AppointmentOut,
    AppointmentResponse
)
from app.services.appointment_service import AppointmentService
from app.db.repositories.appointment_repository import AppointmentRepository

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

@router.post("/", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    *,
    db: Session = Depends(get_db),
    appointment_in: AppointmentCreate,
    current_user = Depends(get_current_user)
):
    """Create a new appointment"""
    try:
        service = AppointmentService(db)
        result = await service.create_appointment(appointment_in, current_user["user_id"])
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[AppointmentOut])
async def list_user_appointments(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """List all appointments for the current user"""
    service = AppointmentService(db)
    return await service.get_user_appointments(current_user["user_id"], skip, limit)

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

@router.get("/{appointment_id}", response_model=AppointmentOut)
async def get_appointment(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    appointment_id: int = Path(..., gt=0, title="The ID of the appointment to get")
):
    """Get a specific appointment by ID"""
    service = AppointmentService(db)
    appointment = await service.get_appointment(appointment_id, current_user["user_id"])

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    return appointment

@router.put("/{appointment_id}", response_model=AppointmentOut)
async def update_appointment(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    appointment_id: int = Path(..., gt=0),
    appointment_in: AppointmentUpdate
):
    """Update an appointment (reschedule)"""
    service = AppointmentService(db)

    try:
        appointment = await service.update_appointment(
            appointment_id,
            appointment_in,
            current_user["user_id"]
        )

        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )

        return appointment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_appointment(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    appointment_id: int = Path(..., gt=0),
    cancellation_reason: str = Body(..., embed=True)
):
    """Cancel an appointment"""
    service = AppointmentService(db)

    try:
        success = await service.cancel_appointment(
            appointment_id,
            current_user["user_id"],
            cancellation_reason
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )

        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
