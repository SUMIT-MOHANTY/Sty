from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field

class AppointmentStatus(str, Enum):
    """Enum for appointment status."""
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    MISSED = "missed"

class UserInfo(BaseModel):
    """Schema for basic user information."""
    id: int
    email: str
    first_name: str
    last_name: str

class ApplicationInfo(BaseModel):
    """Schema for basic application information."""
    id: int
    application_type: str
    application_number: str
    status: str

class TimeSlotInfo(BaseModel):
    """Schema for basic time slot information."""
    id: int
    location_id: int
    start_time: datetime
    end_time: datetime

    class Config:
        orm_mode = True

class AppointmentBase(BaseModel):
    """Base schema for appointment data."""
    user_id: int
    application_id: int
    time_slot_id: int
    status: AppointmentStatus

class AppointmentCreate(AppointmentBase):
    """Schema for creating a new appointment."""
    pass

class AppointmentUpdate(BaseModel):
    """Schema for updating an existing appointment."""
    status: Optional[AppointmentStatus] = None

class AppointmentInDB(AppointmentBase):
    """Schema for appointment data from the database."""
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class AppointmentDetail(AppointmentInDB):
    """Schema for detailed appointment information."""
    user: UserInfo
    application: ApplicationInfo
    time_slot: TimeSlotInfo

    class Config:
        orm_mode = True

class AppointmentListResponse(BaseModel):
    """Response schema for listing appointments."""
    items: List[AppointmentDetail]
    total: int
    page: int
    size: int
