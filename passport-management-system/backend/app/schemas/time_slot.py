from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime, date, time
from enum import Enum

class TimeRange(BaseModel):
    start_time: str  # Format: "HH:MM"
    end_time: str    # Format: "HH:MM"

    @validator('start_time', 'end_time')
    def validate_time_format(cls, v):
        try:
            hour, minute = map(int, v.split(':'))
            if not (0 <= hour < 24 and 0 <= minute < 60):
                raise ValueError("Invalid time format")
        except Exception:
            raise ValueError("Time must be in 'HH:MM' format")
        return v

class WeekDay(int, Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

class TimeSlotBase(BaseModel):
    location_id: int
    start_time: datetime
    end_time: datetime
    capacity: int = Field(..., gt=0)
    is_available: bool = True

class TimeSlotCreate(TimeSlotBase):
    pass

class TimeSlotUpdate(BaseModel):
    capacity: Optional[int] = Field(None, gt=0)
    is_available: Optional[bool] = None

class TimeSlotResponse(TimeSlotBase):
    id: int
    booked_count: Optional[int] = 0

    class Config:
        orm_mode = True

class TimeSlotBatch(BaseModel):
    location_id: int
    start_date: date
    end_date: date
    weekdays: List[WeekDay] = Field(..., min_items=1)
    time_ranges: List[TimeRange] = Field(..., min_items=1)
    capacity: int = Field(..., gt=0)
