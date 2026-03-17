from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..core.database import Base

class ApplicationType(str, enum.Enum):
    NEW = "NEW"
    RENEWAL = "RENEWAL"
    REPLACEMENT = "REPLACEMENT"

class Gender(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    application_type = Column(Enum(ApplicationType), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    place_of_birth = Column(String(100), nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    address = Column(Text, nullable=False)
    phone_number = Column(String(20), nullable=False)
    emergency_contact = Column(String(100), nullable=True)
    previous_passport_number = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="applications")
    documents = relationship("Document", back_populates="application")
    status_updates = relationship("StatusUpdate", back_populates="application", order_by="desc(StatusUpdate.created_at)")
    appointments = relationship("Appointment", back_populates="application")

    @property
    def current_status(self):
        """Return the current status of the application (most recent status update)"""
        if self.status_updates:
            return self.status_updates[0]
        return None
