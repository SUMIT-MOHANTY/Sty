from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..core.database import Base

class TimeSlot(Base):
    __tablename__ = "time_slots"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"))
    is_available = Column(Boolean, default=True)
    max_appointments = Column(Integer, default=1)
    current_appointments = Column(Integer, default=0)

    # Relationships
    location = relationship("Location", back_populates="time_slots")
    appointments = relationship("Appointment", back_populates="time_slot")

    def is_fully_booked(self):
        return self.current_appointments >= self.max_appointments
