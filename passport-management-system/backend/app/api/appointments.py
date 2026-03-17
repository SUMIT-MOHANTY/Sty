from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
import time
import logging

from ..models.appointment import Appointment
from ..models.time_slot import TimeSlot
from ..models.location import Location
from ..models.user import User
from ..schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    TimeSlotResponse,
    AvailableTimeSlotsRequest
)
from ..core.database import get_db
from ..core.security import get_current_user
from ..middleware.rate_limit import rate_limiter
from ..middleware.auth import authenticate_user

# Setup logging for security events
logger = logging.getLogger("api.appointments")

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
    responses={401: {"description": "Unauthorized"}},
)

# Cache to track recent appointment view attempts - mitigate enumeration attacks
recent_appointment_views = {}
MAX_VIEW_ATTEMPTS = 10
VIEW_TIMEOUT = 300  # 5 minutes

@router.get("/available-slots", response_model=List[TimeSlotResponse])
async def get_available_slots(
    location_id: int,
    date: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available appointment slots with security measures."""
    # Apply rate limiting
    client_ip = request.client.host
    await rate_limiter(client_ip, "get_slots", max_requests=20, window_seconds=60)

    try:
        # Validate input date format
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
            if parsed_date < datetime.now().date():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot book appointments in the past"
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )

        # Verify location exists
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location not found"
            )

        # Get all time slots for the location
        all_slots = db.query(TimeSlot).filter(
            TimeSlot.location_id == location_id,
            TimeSlot.date == parsed_date
        ).all()

        # Get booked appointments
        booked_appointments = db.query(Appointment).filter(
            Appointment.location_id == location_id,
            Appointment.appointment_date == parsed_date
        ).all()

        # Get set of booked time slot IDs
        booked_slot_ids = {appointment.time_slot_id for appointment in booked_appointments}

        # Filter out booked slots
        available_slots = [
            TimeSlotResponse(
                id=slot.id,
                location_id=slot.location_id,
                start_time=slot.start_time,
                end_time=slot.end_time,
                date=slot.date
            )
            for slot in all_slots if slot.id not in booked_slot_ids
        ]

        # Log successful retrieval
        logger.info(f"User {current_user.id} retrieved available slots for location {location_id} on {date}")

        return available_slots
    except Exception as e:
        # Log the error but return a generic message to avoid leaking implementation details
        logger.error(f"Error retrieving available slots: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving available slots"
        )

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def book_appointment(
    appointment_data: AppointmentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Book an appointment with security measures."""
    # Apply rate limiting
    client_ip = request.client.host
    await rate_limiter(client_ip, "book_appointment", max_requests=5, window_seconds=60)

    # Validate CSRF token
    csrf_token = request.headers.get("X-CSRF-Token")
    if not csrf_token or not validate_csrf_token(csrf_token, current_user.id):
        logger.warning(f"CSRF token validation failed for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token"
        )

    try:
        # Validate time slot exists
        time_slot = db.query(TimeSlot).filter(TimeSlot.id == appointment_data.time_slot_id).first()
        if not time_slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Time slot not found"
            )

        # Check if the appointment date is in the past
        if time_slot.date < datetime.now().date():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot book appointments in the past"
            )

        # Start a transaction
        try:
            # Check if slot is already booked (double-check for race conditions)
            existing_appointment = db.query(Appointment).filter(
                Appointment.time_slot_id == appointment_data.time_slot_id,
                Appointment.appointment_date == time_slot.date
            ).with_for_update().first()

            if existing_appointment:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This time slot has already been booked"
                )

            # Check if user already has another appointment on the same day
            user_appointment_same_day = db.query(Appointment).filter(
                Appointment.user_id == current_user.id,
                Appointment.appointment_date == time_slot.date
            ).first()

            if user_appointment_same_day:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You already have an appointment scheduled for this day"
                )

            # Create new appointment
            new_appointment = Appointment(
                user_id=current_user.id,
                application_id=appointment_data.application_id,
                location_id=time_slot.location_id,
                time_slot_id=time_slot.id,
                appointment_date=time_slot.date,
                status="scheduled",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            db.add(new_appointment)
            db.commit()
            db.refresh(new_appointment)

            # Log successful booking
            logger.info(f"User {current_user.id} booked appointment {new_appointment.id} for application {appointment_data.application_id}")

            return AppointmentResponse(
                id=new_appointment.id,
                user_id=new_appointment.user_id,
                application_id=new_appointment.application_id,
                location_id=new_appointment.location_id,
                time_slot_id=new_appointment.time_slot_id,
                appointment_date=new_appointment.appointment_date,
                status=new_appointment.status,
                created_at=new_appointment.created_at,
                updated_at=new_appointment.updated_at
            )
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Appointment could not be created due to a conflict"
            )
    except HTTPException:
        raise
    except Exception as e:
        # Log the error but return a generic message
        logger.error(f"Error booking appointment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while booking the appointment"
        )

@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific appointment with security measures."""
    client_ip = request.client.host

    # Prevent enumeration attacks by limiting attempts
    current_time = time.time()
    if client_ip in recent_appointment_views:
        attempts, first_attempt_time = recent_appointment_views[client_ip]
        if current_time - first_attempt_time > VIEW_TIMEOUT:
            # Reset if timeout has elapsed
            recent_appointment_views[client_ip] = (1, current_time)
        elif attempts >= MAX_VIEW_ATTEMPTS:
            # Block if too many attempts
            logger.warning(f"Possible enumeration attack from {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many appointment view attempts. Please try again later."
            )
        else:
            # Increment attempts
            recent_appointment_views[client_ip] = (attempts + 1, first_attempt_time)
    else:
        recent_appointment_views[client_ip] = (1, current_time)

    # Apply rate limiting
    await rate_limiter(client_ip, "get_appointment", max_requests=15, window_seconds=60)

    try:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()

        if not appointment:
            # Don't reveal if an appointment exists or not (to prevent enumeration)
            # But log the actual reason
            logger.info(f"User {current_user.id} attempted to access non-existent appointment {appointment_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )

        # Verify user owns this appointment or is admin
        if appointment.user_id != current_user.id and not current_user.is_admin:
            # Log unauthorized access attempt
            logger.warning(f"Unauthorized access attempt: User {current_user.id} tried to access appointment {appointment_id} belonging to user {appointment.user_id}")
            # Don't reveal if appointment exists (to prevent enumeration)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )

        return AppointmentResponse(
            id=appointment.id,
            user_id=appointment.user_id,
            application_id=appointment.application_id,
            location_id=appointment.location_id,
            time_slot_id=appointment.time_slot_id,
            appointment_date=appointment.appointment_date,
            status=appointment.status,
            created_at=appointment.created_at,
            updated_at=appointment.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving appointment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the appointment"
        )

# Helper function to validate CSRF token
def validate_csrf_token(token: str, user_id: int) -> bool:
    # Actual implementation would validate against stored tokens
    # This is a placeholder for the security concept
    return len(token) > 20  # Simple placeholder validation
