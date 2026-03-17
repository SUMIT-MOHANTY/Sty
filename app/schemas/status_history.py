from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class StatusHistory(BaseModel):
    id: int
    application_id: int
    status: str
    timestamp: datetime
    notes: Optional[str] = None
    created_by: Optional[int] = None

    class Config:
        orm_mode = True

class StatusUpdate(BaseModel):
    application_id: int
    company_name: str
    position_title: str
    status: str
    timestamp: datetime
    notes: Optional[str] = None

    class Config:
        orm_mode = True

class StatusHistoryCreate(BaseModel):
    application_id: int
    status: str
    notes: Optional[str] = None
    created_by: Optional[int] = None

class StatusHistoryUpdate(BaseModel):
    notes: Optional[str] = None
