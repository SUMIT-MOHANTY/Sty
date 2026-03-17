from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class UserPermissionUpdate(BaseModel):
    """User permission update schema"""
    role: str = Field(..., description="User role")
    is_active: Optional[bool] = Field(None, description="User active status")
    permissions: Optional[list] = Field(None, description="User permissions")
