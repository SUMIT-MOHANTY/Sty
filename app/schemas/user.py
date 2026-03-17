from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserRole(str, Enum):
    ADMIN = "admin"
    APPLICANT = "applicant"
    STAFF = "staff"

class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    is_active: bool = True
    role: UserRole = UserRole.APPLICANT

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    password: Optional[str] = None

class UserPermissionUpdate(BaseModel):
    """User permission update schema"""
    role: str = Field(..., description="User role")
    is_active: Optional[bool] = Field(None, description="User active status")
    permissions: Optional[list] = Field(None, description="User permissions")

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
