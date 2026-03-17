from pydantic import BaseModel, EmailStr
from typing import Optional

class TokenData(BaseModel):
    email: Optional[EmailStr] = None

class UserInfo(BaseModel):
    user_id: str
    email: EmailStr
    role: str
    first_name: str
    last_name: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserInfo
