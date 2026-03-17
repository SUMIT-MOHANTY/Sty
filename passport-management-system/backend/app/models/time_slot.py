from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class TimeSlot(Base):
    __tablename__ = "time_slots"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), index=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    max_appointments = Column(Integer, nullable=False, default=1)
    current_appointments = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    location = relationship("Location", back_populates="time_slots")
    appointments = relationship("Appointment", back_populates="time_slot")

    def is_available(self):
        """Check if the time slot is available for booking."""
        return self.is_active and self.current_appointments < self.max_appointments

    def increment_appointments(self):
        """Increment the current appointment count when a new appointment is booked."""
        if self.current_appointments < self.max_appointments:
            self.current_appointments += 1
            return True
        return False

    def decrement_appointments(self):
        """Decrement the current appointment count when an appointment is cancelled."""
        if self.current_appointments > 0:
            self.current_appointments -= 1
            return True
        return False
