from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum

class ApplicationStatus(str, Enum):
    SUBMITTED = "submitted"
    DOCUMENT_VERIFICATION = "document_verification"
    BACKGROUND_CHECK = "background_check"
    PROCESSING = "processing"
    READY_FOR_PICKUP = "ready_for_pickup"
    COMPLETED = "completed"
    REJECTED = "rejected"

class ApplicationBase(BaseModel):
    application_type: str
    notes: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    pass

class StatusUpdateBase(BaseModel):
    status: str
    comment: Optional[str] = None
    created_at: datetime
    created_by: int

    class Config:
        orm_mode = True

class ApplicationResponse(ApplicationBase):
    id: int
    user_id: int
    application_number: str
    status: ApplicationStatus
    submitted_at: datetime
    last_updated_at: datetime

    class Config:
        orm_mode = True

class ApplicationStatusResponse(BaseModel):
    application: ApplicationResponse
    current_status: ApplicationStatus
    status_history: List[StatusUpdateBase]

    class Config:
        orm_mode = True
