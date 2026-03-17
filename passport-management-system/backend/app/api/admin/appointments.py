from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta

from app.core.database import get_db
from app.middleware.auth import get_current_admin_user
from app.models.user import User
from app.models.appointment import Appointment
from app.models.time_slot import TimeSlot
from app.models.location import Location
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
    AppointmentAdminResponse,
    AppointmentStatistics
)
from app.schemas.time_slot import (
    TimeSlotCreate,
    TimeSlotResponse,
    TimeSlotUpdate,
    TimeSlotBatch
)

router = APIRouter()

# ----- Time Slot Management Endpoints -----

@router.post("/timeslots/", response_model=TimeSlotResponse, status_code=status.HTTP_201_CREATED)
def create_time_slot(
    time_slot: TimeSlotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new time slot (admin only)"""
    # Check if location exists
    location = db.query(Location).filter(Location.id == time_slot.location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )

    # Check if time slot already exists for this time and location
    existing_slot = db.query(TimeSlot).filter(
        TimeSlot.location_id == time_slot.location_id,
        TimeSlot.start_time == time_slot.start_time,
        TimeSlot.end_time == time_slot.end_time
    ).first()

    if existing_slot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A time slot with this date, time, and location already exists"
        )

    # Create new time slot
    db_time_slot = TimeSlot(
        location_id=time_slot.location_id,
        start_time=time_slot.start_time,
        end_time=time_slot.end_time,
        capacity=time_slot.capacity,
        is_available=time_slot.is_available
    )
    db.add(db_time_slot)
    db.commit()
    db.refresh(db_time_slot)
    return db_time_slot

@router.post("/timeslots/batch/", response_model=List[TimeSlotResponse])
def create_time_slots_batch(
    batch: TimeSlotBatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create multiple time slots at once (admin only)"""
    location = db.query(Location).filter(Location.id == batch.location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )

    created_slots = []
    current_date = batch.start_date

    # Create time slots for each day in the date range
    while current_date <= batch.end_date:
        # Skip days that are not in the specified weekdays
        if current_date.weekday() in batch.weekdays:
            for time_range in batch.time_ranges:
                start_hour, start_minute = map(int, time_range.start_time.split(':'))
                end_hour, end_minute = map(int, time_range.end_time.split(':'))

                # Create datetime objects for start and end times
                start_datetime = datetime.combine(
                    current_date,
                    datetime.min.time().replace(hour=start_hour, minute=start_minute)
                )
                end_datetime = datetime.combine(
                    current_date,
                    datetime.min.time().replace(hour=end_hour, minute=end_minute)
                )

                # Check if slot already exists
                existing_slot = db.query(TimeSlot).filter(
                    TimeSlot.location_id == batch.location_id,
                    TimeSlot.start_time == start_datetime,
                    TimeSlot.end_time == end_datetime
                ).first()

                if not existing_slot:
                    # Create the new slot
                    db_time_slot = TimeSlot(
                        location_id=batch.location_id,
                        start_time=start_datetime,
                        end_time=end_datetime,
                        capacity=batch.capacity,
                        is_available=True
                    )
                    db.add(db_time_slot)
                    created_slots.append(db_time_slot)

        current_date += timedelta(days=1)

    db.commit()

    # Refresh all created slots
    for slot in created_slots:
        db.refresh(slot)

    return created_slots

@router.get("/timeslots/", response_model=List[TimeSlotResponse])
def list_time_slots(
    location_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    is_available: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """List all time slots with filtering options (admin only)"""
    query = db.query(TimeSlot)

    # Apply filters
    if location_id:
        query = query.filter(TimeSlot.location_id == location_id)

    if start_date:
        # Convert date to datetime for comparison
        start_datetime = datetime.combine(start_date, datetime.min.time())
        query = query.filter(TimeSlot.start_time >= start_datetime)

    if end_date:
        # Convert date to datetime for comparison
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.filter(TimeSlot.start_time <= end_datetime)

    if is_available is not None:
        query = query.filter(TimeSlot.is_available == is_available)

    # Apply pagination
    query = query.offset(skip).limit(limit)

    return query.all()

@router.put("/timeslots/{time_slot_id}", response_model=TimeSlotResponse)
def update_time_slot(
    time_slot_id: int,
    time_slot_update: TimeSlotUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update a time slot (admin only)"""
    db_time_slot = db.query(TimeSlot).filter(TimeSlot.id == time_slot_id).first()
    if not db_time_slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time slot not found"
        )

    # Update the attributes
    for key, value in time_slot_update.dict(exclude_unset=True).items():
        setattr(db_time_slot, key, value)

    db.commit()
    db.refresh(db_time_slot)
    return db_time_slot

@router.delete("/timeslots/{time_slot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_time_slot(
    time_slot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a time slot (admin only)"""
    db_time_slot = db.query(TimeSlot).filter(TimeSlot.id == time_slot_id).first()
    if not db_time_slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time slot not found"
        )

    # Check if the time slot has appointments
    appointments = db.query(Appointment).filter(Appointment.time_slot_id == time_slot_id).count()
    if appointments > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a time slot with existing appointments"
        )

    db.delete(db_time_slot)
    db.commit()
    return None

# ----- Appointment Management Endpoints -----

@router.get("/appointments/", response_model=List[AppointmentAdminResponse])
def list_appointments(
    location_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """List all appointments with filtering options (admin only)"""
    query = db.query(Appointment).join(TimeSlot)

    # Apply filters
    if location_id:
        query = query.filter(TimeSlot.location_id == location_id)

    if date_from:
        date_from_dt = datetime.combine(date_from, datetime.min.time())
        query = query.filter(TimeSlot.start_time >= date_from_dt)

    if date_to:
        date_to_dt = datetime.combine(date_to, datetime.max.time())
        query = query.filter(TimeSlot.start_time <= date_to_dt)

    if status:
        query = query.filter(Appointment.status == status)

    if user_id:
        query = query.filter(Appointment.user_id == user_id)

    # Apply pagination
    query = query.offset(skip).limit(limit)

    return query.all()

@router.get("/appointments/{appointment_id}", response_model=AppointmentAdminResponse)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get a specific appointment by ID (admin only)"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    return appointment

@router.put("/appointments/{appointment_id}", response_model=AppointmentAdminResponse)
def update_appointment(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update an appointment (admin only)"""
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    # If changing time slot, validate it
    if appointment_update.time_slot_id and appointment_update.time_slot_id != db_appointment.time_slot_id:
        new_time_slot = db.query(TimeSlot).filter(TimeSlot.id == appointment_update.time_slot_id).first()
        if not new_time_slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Time slot not found"
            )

        if not new_time_slot.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Time slot is not available"
            )

        # Check if the time slot has reached capacity
        current_appointments = db.query(Appointment).filter(
            Appointment.time_slot_id == appointment_update.time_slot_id,
            Appointment.status != "cancelled"
        ).count()

        if current_appointments >= new_time_slot.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Time slot is at full capacity"
            )

    # Update the appointment
    for key, value in appointment_update.dict(exclude_unset=True).items():
        setattr(db_appointment, key, value)

    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@router.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Cancel an appointment (admin only)"""
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    # Instead of deleting, mark as cancelled
    db_appointment.status = "cancelled"
    db_appointment.cancellation_date = datetime.utcnow()
    db.commit()

    return None

@router.get("/appointments/statistics/", response_model=AppointmentStatistics)
def get_appointment_statistics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    location_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get appointment statistics (admin only)"""
    # Base query
    base_query = db.query(Appointment).join(TimeSlot)

    # Apply filters
    if start_date:
        start_datetime = datetime.combine(start_date, datetime.min.time())
        base_query = base_query.filter(TimeSlot.start_time >= start_datetime)

    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
        base_query = base_query.filter(TimeSlot.start_time <= end_datetime)

    if location_id:
        base_query = base_query.filter(TimeSlot.location_id == location_id)

    # Calculate statistics
    total = base_query.count()

    completed = base_query.filter(Appointment.status == "completed").count()
    scheduled = base_query.filter(Appointment.status == "scheduled").count()
    cancelled = base_query.filter(Appointment.status == "cancelled").count()
    no_show = base_query.filter(Appointment.status == "no_show").count()

    # Calculate monthly statistics if date range spans multiple months
    monthly_stats = {}
    if start_date and end_date and (end_date.year > start_date.year or end_date.month > start_date.month):
        current_date = start_date.replace(day=1)
        while current_date <= end_date:
            month_key = f"{current_date.year}-{current_date.month:02d}"
            next_month = current_date.month + 1 if current_date.month < 12 else 1
            next_year = current_date.year if current_date.month < 12 else current_date.year + 1
            next_month_date = date(next_year, next_month, 1)

            month_start = datetime.combine(current_date, datetime.min.time())
            month_end = datetime.combine(next_month_date, datetime.min.time()) - timedelta(seconds=1)

            monthly_count = base_query.filter(
                TimeSlot.start_time >= month_start,
                TimeSlot.start_time <= month_end
            ).count()

            monthly_stats[month_key] = monthly_count
            current_date = next_month_date

    return {
        "total": total,
        "completed": completed,
        "scheduled": scheduled,
        "cancelled": cancelled,
        "no_show": no_show,
        "monthly_stats": monthly_stats
    }
