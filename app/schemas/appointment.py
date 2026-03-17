from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, validator
import re

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    MISSED = "missed"
    RESCHEDULED = "rescheduled"

class AppointmentBase(BaseModel):
    user_id: int
    application_id: int
    location_id: int
    appointment_date: datetime
    notes: Optional[str] = None

    @validator("appointment_date")
    def validate_appointment_date(cls, v):
        if v < datetime.utcnow():
            raise ValueError("Appointment date cannot be in the past")
        # Ensure appointment during business hours (9 AM - 5 PM)
        if v.hour < 9 or v.hour >= 17:
            raise ValueError("Appointments must be scheduled between 9 AM and 5 PM")
        # Ensure appointment on weekdays only
        if v.weekday() >= 5:  # 5=Saturday, 6=Sunday
            raise ValueError("Appointments must be scheduled on weekdays")
        return v

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    appointment_date: Optional[datetime] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = Field(None, max_length=500)

    @validator("cancellation_reason")
    def validate_cancellation_reason(cls, v, values):
        if values.get("status") == AppointmentStatus.CANCELLED and not v:
            raise ValueError("Cancellation reason is required when cancelling an appointment")

        # Sanitize the input to prevent XSS
        if v:
            # Remove potentially dangerous HTML/script tags
            v = re.sub(r'<[^>]*>', '', v)
        return v

class AppointmentInDB(AppointmentBase):
    id: int
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class AppointmentResponse(AppointmentBase):
    id: int
    status: AppointmentStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class AppointmentOut(AppointmentInDB):
    location_name: Optional[str] = None
    is_modifiable: bool = True

    # Remove internal identifiers for external responses
    class Config:
        orm_mode = True
        exclude = {"created_by", "updated_by", "secure_id"}
