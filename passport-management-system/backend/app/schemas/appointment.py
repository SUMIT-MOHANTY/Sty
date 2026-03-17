from pydantic import BaseModel, validator
from datetime import date, time, datetime
from typing import Optional

class TimeSlotBase(BaseModel):
    location_id: int
    start_time: time
    end_time: time
    date: date

    @validator('date')
    def date_not_in_past(cls, v):
        if v < datetime.now().date():
            raise ValueError('Cannot book appointments in the past')
        return v

    @validator('end_time')
    def end_time_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

class TimeSlotCreate(TimeSlotBase):
    pass

class TimeSlotResponse(TimeSlotBase):
    id: int

    class Config:
        orm_mode = True

class AvailableTimeSlotsRequest(BaseModel):
    location_id: int
    date: date

class AppointmentBase(BaseModel):
    application_id: int
    time_slot_id: int

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentResponse(BaseModel):
    id: int
    user_id: int
    application_id: int
    location_id: int
    time_slot_id: int
    appointment_date: date
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
