from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, Path
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentOut
from app.services.appointment_service import AppointmentService

router = APIRouter()

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
