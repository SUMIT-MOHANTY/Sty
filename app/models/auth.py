from pydantic import BaseModel, EmailStr, Field, validator
import re
from typing import Optional

class UserRegistration(BaseModel):
    """
    Pydantic model for user registration request validation.

    Attributes:
        email: User's email address
        password: User's password
        confirm_password: Password confirmation
        first_name: User's first name
        last_name: User's last name
    """
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str
    first_name: str
    last_name: str

    @validator('password')
    def password_strength(cls, v):
        """Validate password meets complexity requirements."""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate that password and confirm_password match."""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class UserResponse(BaseModel):
    """
    Pydantic model for user registration response.

    Attributes:
        user_id: The ID of the registered user
        email: User's email address
        message: Success message
    """
    user_id: str
    email: str
    message: str

class EmailVerificationRequest(BaseModel):
    """
    Pydantic model for email verification request.

    Attributes:
        token: The verification token
    """
    token: str

class EmailVerificationResponse(BaseModel):
    """
    Pydantic model for email verification response.

    Attributes:
        message: Success message
    """
    message: str
