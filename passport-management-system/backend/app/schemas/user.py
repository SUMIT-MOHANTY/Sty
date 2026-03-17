from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Union
from datetime import datetime
import uuid
import re

class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)

class UserCreate(UserBase):
    """Schema for creating a new user - includes password validation"""
    password: str = Field(..., min_length=8)
    confirm_password: str

    @validator('password')
    def password_strength(cls, v):
        """Enforce strong password policy"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[^A-Za-z0-9]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        """Ensure password and confirm_password match"""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    is_active: Optional[bool] = None

class AdminUserUpdate(UserUpdate):
    """Admin-only schema for updating users with additional fields"""
    role: Optional[str] = Field(None, pattern="^(regular|admin)$")
    is_verified: Optional[bool] = None

class UserPasswordUpdate(BaseModel):
    """Schema for updating user password"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    @validator('new_password')
    def password_strength(cls, v):
        """Enforce strong password policy"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[^A-Za-z0-9]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        """Ensure password and confirm_password match"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class UserInDB(UserBase):
    """Database representation of a user (for internal use)"""
    id: uuid.UUID
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True

class UserResponse(UserBase):
    """User information returned to the client (public-facing)"""
    id: uuid.UUID
    role: str
    is_active: bool
    is_verified: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    """JWT token schema"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """JWT token payload data"""
    user_id: Optional[str] = None
    role: Optional[str] = None
