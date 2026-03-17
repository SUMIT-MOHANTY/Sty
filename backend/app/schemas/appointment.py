from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from backend.app.models.appointment import AppointmentStatus

class AppointmentCreate(BaseModel):
    application_id: UUID
    location_id: str
    scheduled_date: datetime

class AppointmentResponse(BaseModel):
    id: UUID
    appointment_number: str
    user_id: UUID
    application_id: UUID
    location_id: str
    scheduled_date: datetime
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
