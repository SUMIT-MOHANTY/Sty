from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from backend.app.models.application import ApplicationStatus

class ApplicationCreate(BaseModel):
    personal_details: Dict[str, Any]
    contact_details: Dict[str, Any]
    passport_details: Optional[Dict[str, Any]] = None
    additional_info: Optional[Dict[str, Any]] = None

class ApplicationResponse(BaseModel):
    id: UUID
    application_number: str
    user_id: UUID
    status: ApplicationStatus
    personal_details: Dict[str, Any]
    contact_details: Dict[str, Any]
    passport_details: Optional[Dict[str, Any]] = None
    additional_info: Optional[Dict[str, Any]] = None
    submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
