from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.base import Base

class ApplicationStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    ADDITIONAL_INFO_REQUIRED = "ADDITIONAL_INFO_REQUIRED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"

class Application(Base):
    __tablename__ = "applications"

    application_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    application_number = Column(String(20), unique=True, nullable=False)
    passport_type = Column(String(20), nullable=False)
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.SUBMITTED, nullable=False)
    admin_notes = Column(Text, nullable=True)
    assigned_to = Column(String, ForeignKey("users.user_id"), nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="applications")
    admin = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_applications")
    documents = relationship("Document", back_populates="application")
    personal_details = relationship("PersonalDetails", back_populates="application", uselist=False)
    contact_details = relationship("ContactDetails", back_populates="application", uselist=False)
    passport_details = relationship("PassportDetails", back_populates="application", uselist=False)
    appointments = relationship("Appointment", back_populates="application")

    def update_status(self, new_status):
        self.status = new_status
        self.last_updated_at = datetime.utcnow()

# Alias for backward compatibility
PassportApplication = Application
