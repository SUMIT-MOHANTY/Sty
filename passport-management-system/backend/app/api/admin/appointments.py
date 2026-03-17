"""
Admin routes for appointment management.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...middleware.auth import get_current_admin_user
from ...models.user import User
from ...models.appointment import Appointment
from ...schemas.appointment import (
    AppointmentAdminResponse,
    AppointmentListParams,
    AppointmentStatusUpdate
)

router = APIRouter(prefix="/appointments")

@router.get("/", response_model=List[AppointmentAdminResponse])
async def get_all_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    location_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """
    Retrieve all appointments with filtering options.
    Only accessible to admin users.
    """
    query = db.query(Appointment)

    # Apply filters if provided
    if status:
        query = query.filter(Appointment.status == status)

    if location_id:
        query = query.filter(Appointment.location_id == location_id)

    if date_from:
        query = query.filter(Appointment.appointment_date >= date_from)

    if date_to:
        query = query.filter(Appointment.appointment_date <= date_to)

    # Apply pagination
    appointments = query.offset(skip).limit(limit).all()

    return appointments

@router.put("/{appointment_id}/status", response_model=AppointmentAdminResponse)
async def update_appointment_status(
    appointment_id: int,
    status_update: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update the status of an appointment.
    Only accessible to admin users.
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment with ID {appointment_id} not found"
        )

    appointment.status = status_update.status
    appointment.admin_notes = status_update.notes

    db.commit()
    db.refresh(appointment)

    return appointment
