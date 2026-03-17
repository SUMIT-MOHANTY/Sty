from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

class ApplicationStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ADDITIONAL_INFO_NEEDED = "additional_info_needed"
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING_PAYMENT = "pending_payment"
    COMPLETED = "completed"

class PassportType(str, Enum):
    REGULAR = "regular"
    DIPLOMATIC = "diplomatic"
    OFFICIAL = "official"
    EMERGENCY = "emergency"

class ApplicationBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birth_date: datetime
    passport_type: PassportType = PassportType.REGULAR
    notes: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    admin_notes: Optional[str] = None
    review_date: Optional[datetime] = None

class ApplicationSearchQuery(BaseModel):
    query: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None

class ApplicationResponse(ApplicationBase):
    id: int
    status: ApplicationStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    review_date: Optional[datetime] = None
    admin_notes: Optional[str] = None

    class Config:
        orm_mode = True

class ApplicationPagination(BaseModel):
    total: int
    items: List[ApplicationResponse]
    page: int
    size: int
    pages: int
