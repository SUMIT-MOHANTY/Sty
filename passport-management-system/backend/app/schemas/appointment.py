from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Union
from datetime import datetime
from enum import Enum

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class AppointmentBase(BaseModel):
    time_slot_id: int
    application_id: int
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    time_slot_id: Optional[int] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None

class AppointmentResponse(AppointmentBase):
    id: int
    user_id: int
    status: AppointmentStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    cancellation_date: Optional[datetime] = None

    class Config:
        orm_mode = True

class AppointmentAdminResponse(AppointmentResponse):
    # Additional fields for admin view
    user_email: str
    user_full_name: str
    location_name: str
    appointment_date: datetime
    appointment_end: datetime

    class Config:
        orm_mode = True

class AppointmentStatistics(BaseModel):
    total: int
    completed: int
    scheduled: int
    cancelled: int
    no_show: int
    monthly_stats: Dict[str, int] = {}
