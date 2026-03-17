from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator

class TimeSlotBase(BaseModel):
    """Base schema for time slot data."""
    location_id: int
    start_time: datetime
    end_time: datetime
    capacity: int

    @validator("end_time")
    def end_time_after_start_time(cls, v, values):
        if "start_time" in values and v <= values["start_time"]:
            raise ValueError("End time must be after start time")
        return v

    @validator("capacity")
    def capacity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Capacity must be greater than 0")
        return v

class TimeSlotCreate(TimeSlotBase):
    """Schema for creating a new time slot."""
    pass

class TimeSlotUpdate(BaseModel):
    """Schema for updating an existing time slot."""
    location_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    capacity: Optional[int] = None

    @validator("capacity")
    def capacity_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Capacity must be greater than 0")
        return v

class TimeSlotInDB(TimeSlotBase):
    """Schema for time slot data from the database."""
    id: int

    class Config:
        orm_mode = True

class TimeSlotWithBookings(TimeSlotInDB):
    """Schema for time slot with booking information."""
    booked_count: int
    available: bool

    class Config:
        orm_mode = True

class TimeSlotListResponse(BaseModel):
    """Response schema for listing time slots."""
    items: List[TimeSlotWithBookings]
    total: int
    page: int
    size: int
