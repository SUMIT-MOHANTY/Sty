from typing import Optional

from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: Optional[str] = None

    class Config:
        orm_mode = True

class User(UserInDBBase):
    role: Optional[str] = None

class UserInDB(UserInDBBase):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
