import enum
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

from app.db.base import Base

class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    MISSED = "missed"

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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="appointments")
    application = relationship("Application", back_populates="appointments")
    slot = relationship("AppointmentSlot", back_populates="appointments")
    location = relationship("Location", back_populates="appointments")
