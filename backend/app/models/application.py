from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, validator
from uuid import UUID

class ApplicationStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ADDITIONAL_INFO_REQUIRED = "additional_info_required"
    APPROVED = "approved"
    REJECTED = "rejected"

class DocumentType(str, Enum):
    IDENTITY = "identity"
    PROOF_OF_ADDRESS = "proof_of_address"
    PHOTO = "photo"
    SUPPORTING_DOCUMENT = "supporting_document"

class DocumentBase(BaseModel):
    document_type: DocumentType
    filename: str
    file_path: Optional[str] = None
    mime_type: str

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: UUID
    application_id: UUID
    uploaded_at: datetime

    class Config:
        orm_mode = True

class ApplicationBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    date_of_birth: datetime
    phone_number: str = Field(..., min_length=5, max_length=20)
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    previous_passport: bool = False
    previous_passport_number: Optional[str] = None
    emergency_contact_name: str
    emergency_contact_phone: str
    emergency_contact_relation: str

class ApplicationCreate(ApplicationBase):
    pass

    @validator("date_of_birth")
    def validate_date_of_birth(cls, v):
        if v > datetime.now():
            raise ValueError("Date of birth cannot be in the future")
        return v

class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None

class ApplicationResponse(ApplicationBase):
    id: UUID
    user_id: UUID
    status: ApplicationStatus
    created_at: datetime
    updated_at: datetime
    documents: List[DocumentResponse] = []

    class Config:
        orm_mode = True
