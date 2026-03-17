from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

# Schema for user registration
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    first_name: str
    last_name: str

# Schema for user response data
class UserResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    is_active: bool
    is_email_verified: bool

    class Config:
        orm_mode = True
