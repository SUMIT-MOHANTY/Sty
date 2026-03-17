from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base

class ApplicationStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    DOCUMENT_VERIFICATION = "document_verification"
    BACKGROUND_CHECK = "background_check"
    PROCESSING = "processing"
    READY_FOR_PICKUP = "ready_for_pickup"
    COMPLETED = "completed"
    REJECTED = "rejected"

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    application_number = Column(String, unique=True, index=True)
    application_type = Column(String)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.SUBMITTED)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    last_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="applications")
    documents = relationship("Document", back_populates="application")
    status_updates = relationship("StatusUpdate", back_populates="application", order_by="StatusUpdate.created_at")
    appointments = relationship("Appointment", back_populates="application")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "application_number": self.application_number,
            "application_type": self.application_type,
            "status": self.status,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "last_updated_at": self.last_updated_at.isoformat() if self.last_updated_at else None,
            "notes": self.notes
        }
