from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator

class UserBase(BaseModel):
    email: EmailStr

class UserLogin(UserBase):
    password: str

class UserRegister(UserBase):
    password: str
    confirm_password: str
    first_name: str
    last_name: str

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

class UserResponse(UserBase):
    user_id: str
    first_name: str
    last_name: str
    role: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None
