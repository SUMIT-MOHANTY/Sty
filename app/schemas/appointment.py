from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field

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

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    status: Optional[str] = None

class Appointment(AppointmentBase):
    id: UUID
    user_id: UUID
    location_id: UUID
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class AppointmentResponse(Appointment):
    location_name: Optional[str] = None
    location_address: Optional[str] = None

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
