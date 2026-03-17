from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from backend.app.db.session import get_db
from backend.app.schemas.appointment import AppointmentCreate, AppointmentResponse
from backend.app.services.appointment_service import create_appointment, get_user_appointments
from backend.app.core.security import get_current_user
from backend.app.schemas.user import User

router = APIRouter()

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def book_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Book a new appointment.
    """
    return create_appointment(db=db, appointment=appointment, user_id=current_user.id)

@router.get("/", response_model=List[AppointmentResponse])
def read_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve appointments for the current user.
    """
    return get_user_appointments(db=db, user_id=current_user.id, skip=skip, limit=limit)
