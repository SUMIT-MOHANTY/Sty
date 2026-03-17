from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship

from app.db.base import Base

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    RESCHEDULED = "rescheduled"

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)

    # Date and time fields
    appointment_date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Status tracking
    status = Column(String, default=AppointmentStatus.SCHEDULED)
    cancellation_reason = Column(Text, nullable=True)

    # Audit fields
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))

    # Security field to prevent timing attacks during DB lookups
    secure_id = Column(String, unique=True, index=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="appointments")
    application = relationship("Application", back_populates="appointments")
    location = relationship("Location")

    def is_modifiable(self) -> bool:
        """Check if appointment can be modified (not too close to appointment time)"""
        if self.status != AppointmentStatus.SCHEDULED:
            return False

        time_until_appointment = self.appointment_date - datetime.utcnow()
        # Minimum 24 hours before appointment for changes
        return time_until_appointment.total_seconds() > 86400
