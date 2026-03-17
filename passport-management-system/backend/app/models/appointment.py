from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), unique=True, index=True)
    time_slot_id = Column(Integer, ForeignKey("time_slots.id"), index=True)
    location_id = Column(Integer, ForeignKey("locations.id"))
    status = Column(String(50), nullable=False, default="scheduled")  # scheduled, completed, cancelled, missed
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="appointments")
    application = relationship("Application", back_populates="appointment")
    time_slot = relationship("TimeSlot", back_populates="appointments")
    location = relationship("Location", back_populates="appointments")

    def cancel(self):
        """Cancel an appointment."""
        if self.status == "scheduled":
            self.status = "cancelled"
            # Free up the time slot
            self.time_slot.decrement_appointments()
            return True
        return False

    def complete(self):
        """Mark an appointment as completed."""
        if self.status == "scheduled":
            self.status = "completed"
            return True
        return False

    def miss(self):
        """Mark an appointment as missed."""
        if self.status == "scheduled":
            self.status = "missed"
            return True
        return False
