from typing import Optional, List
from pydantic import BaseModel
from datetime import date, datetime
from enum import Enum

class ApplicationType(str, Enum):
    NEW = "NEW"
    RENEWAL = "RENEWAL"
    REPLACEMENT = "REPLACEMENT"

class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class ApplicationBase(BaseModel):
    application_type: ApplicationType
    first_name: str
    last_name: str
    date_of_birth: date
    place_of_birth: str
    gender: Gender
    address: str
    phone_number: str
    emergency_contact: Optional[str] = None
    previous_passport_number: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationResponse(ApplicationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
