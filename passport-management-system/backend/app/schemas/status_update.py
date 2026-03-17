from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class StatusUpdateBase(BaseModel):
    status: str
    notes: Optional[str] = None

class StatusUpdateCreate(StatusUpdateBase):
    application_id: int

class StatusUpdateResponse(StatusUpdateBase):
    id: int
    application_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
