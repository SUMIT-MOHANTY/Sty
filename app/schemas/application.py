from typing import List, Optional
from datetime import date
from pydantic import BaseModel, EmailStr, validator, Field
import re

class DocumentBase(BaseModel):
    document_type: str
    filename: str
    file_path: str
    uploaded_at: Optional[date] = None

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: int
    application_id: int

    class Config:
        orm_mode = True

class ApplicationBase(BaseModel):
    passport_type: str = Field(..., description="Type of passport being applied for")
    first_name: str = Field(..., min_length=1, max_length=100, description="Applicant's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Applicant's last name")
    date_of_birth: date = Field(..., description="Applicant's date of birth")
    gender: str = Field(..., description="Applicant's gender")
    address_line1: str = Field(..., min_length=1, max_length=255, description="Address line 1")
    address_line2: Optional[str] = Field(None, max_length=255, description="Address line 2")
    city: str = Field(..., min_length=1, max_length=100, description="City")
    state: str = Field(..., min_length=1, max_length=100, description="State")
    postal_code: str = Field(..., description="Postal code")
    country: str = Field(..., description="Country")
    phone_number: str = Field(..., description="Phone number")
    email: EmailStr = Field(..., description="Email address")
    emergency_contact_name: str = Field(..., min_length=1, max_length=200, description="Emergency contact name")
    emergency_contact_phone: str = Field(..., description="Emergency contact phone")
    has_previous_passport: bool = Field(..., description="Whether applicant has had a passport before")
    previous_passport_number: Optional[str] = Field(None, description="Previous passport number if applicable")

    # Validators
    @validator('date_of_birth')
    def validate_dob(cls, v):
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 0:
            raise ValueError('Date of birth cannot be in the future')
        return v

    @validator('phone_number', 'emergency_contact_phone')
    def validate_phone_number(cls, v):
        # Simple validation - real implementation would be more sophisticated
        pattern = r'^\+?[0-9]{10,15}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid phone number format')
        return v

    @validator('postal_code')
    def validate_postal_code(cls, v):
        # Simple validation - would need to be country-specific in a real app
        if not re.match(r'^[0-9a-zA-Z-\s]{3,10}$', v):
            raise ValueError('Invalid postal code format')
        return v

    @validator('passport_type')
    def validate_passport_type(cls, v):
        valid_types = ['regular', 'official', 'diplomatic', 'emergency']
        if v.lower() not in valid_types:
            raise ValueError(f'Passport type must be one of: {", ".join(valid_types)}')
        return v.lower()

class ApplicationCreate(ApplicationBase):
    user_id: Optional[int] = None

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class Application(ApplicationBase):
    id: int
    user_id: int
    status: str
    submitted_at: date
    documents: List[Document] = []

    class Config:
        orm_mode = True
