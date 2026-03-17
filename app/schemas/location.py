from typing import Optional
from pydantic import BaseModel

class LocationBase(BaseModel):
    name: str
    address: str
    city: str
    state: str
    postal_code: str
    country: str
    phone: Optional[str] = None
    email: Optional[str] = None

class LocationCreate(LocationBase):
    pass

class LocationResponse(LocationBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
