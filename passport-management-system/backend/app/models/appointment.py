from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=True)
    time_slot_id = Column(Integer, ForeignKey("time_slots.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))
    status = Column(String, default="Scheduled")  # Scheduled, Completed, Cancelled, Rescheduled
    booking_date = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="appointments")
    application = relationship("Application", back_populates="appointment")
    time_slot = relationship("TimeSlot", back_populates="appointments")
    location = relationship("Location", back_populates="appointments")
