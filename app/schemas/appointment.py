from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, UUID
from pydantic import BaseModel, Field, validator
import re

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    MISSED = "missed"
    RESCHEDULED = "rescheduled"

class AppointmentSlotBase(BaseModel):
    location_id: UUID
    start_time: datetime
    end_time: datetime
    max_appointments: int = 1
    is_available: bool = True

class AppointmentSlotCreate(AppointmentSlotBase):
    pass

class AppointmentSlot(AppointmentSlotBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class AppointmentBase(BaseModel):
    slot_id: UUID
    application_id: UUID
    user_id: UUID
    location_id: UUID
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

class Appointment(AppointmentBase):
    id: UUID
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class AppointmentInDB(AppointmentBase):
    id: UUID
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class AppointmentResponse(Appointment):
    location_name: Optional[str] = None
    location_address: Optional[str] = None

class AppointmentOut(AppointmentInDB):
    location_name: Optional[str] = None
    is_modifiable: bool = True

    # Remove internal identifiers for external responses
    class Config:
        orm_mode = True
        exclude = {"created_by", "updated_by", "secure_id"}

class UserInfo(BaseModel):
    id: UUID
    email: str
    first_name: str
    last_name: str

class ApplicationInfo(BaseModel):
    id: UUID
    type: str
    status: str

class AppointmentAdminResponse(Appointment):
    user: UserInfo
    application: ApplicationInfo

class AppointmentStats(BaseModel):
    total: int
    scheduled: int
    completed: int
    cancelled: int
    missed: int

class AppointmentsTimeRange(BaseModel):
    start_date: datetime = Field(..., description="Start date for appointment range")
    end_date: datetime = Field(..., description="End date for appointment range")
    location_id: Optional[UUID] = Field(None, description="Filter by location")
    status: Optional[str] = Field(None, description="Filter by appointment status")
