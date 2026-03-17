import enum
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

from app.db.base import Base

class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    MISSED = "missed"
    RESCHEDULED = "rescheduled"

class AppointmentSlot(Base):
    __tablename__ = "appointment_slots"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    location_id = Column(PostgresUUID(as_uuid=True), ForeignKey("locations.id"))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    max_appointments = Column(Integer, nullable=False, default=1)
    is_available = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    location = relationship("Location", back_populates="appointment_slots")
    appointments = relationship("Appointment", back_populates="slot")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    application_id = Column(PostgresUUID(as_uuid=True), ForeignKey("applications.id"), nullable=False)
    slot_id = Column(PostgresUUID(as_uuid=True), ForeignKey("appointment_slots.id"), nullable=False)
    location_id = Column(PostgresUUID(as_uuid=True), ForeignKey("locations.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    cancellation_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    secure_id = Column(String, unique=True, index=True)

    # Audit fields
    created_by = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="appointments")
    application = relationship("Application", back_populates="appointments")
    slot = relationship("AppointmentSlot", back_populates="appointments")
    location = relationship("Location", back_populates="appointments")

    def is_modifiable(self) -> bool:
        """Check if appointment can be modified (not too close to appointment time)"""
        if self.status != AppointmentStatus.SCHEDULED:
            return False

        time_until_appointment = self.start_time - datetime.utcnow()
        # Minimum 24 hours before appointment for changes
        return time_until_appointment.total_seconds() > 86400
