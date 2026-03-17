import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.application import ApplicationStatus, DocumentType
from app.core.database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    phone_number = Column(String(20), nullable=False)
    address_line_1 = Column(String(255), nullable=False)
    address_line_2 = Column(String(255))
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False)
    previous_passport = Column(Boolean, default=False)
    previous_passport_number = Column(String(50))
    emergency_contact_name = Column(String(100), nullable=False)
    emergency_contact_phone = Column(String(20), nullable=False)
    emergency_contact_relation = Column(String(100), nullable=False)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.SUBMITTED, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="applications")
    documents = relationship("Document", back_populates="application", cascade="all, delete-orphan")
    status_updates = relationship("StatusUpdate", back_populates="application", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    mime_type = Column(String(100), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    application = relationship("Application", back_populates="documents")

class StatusUpdate(Base):
    __tablename__ = "status_updates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False)
    status = Column(Enum(ApplicationStatus), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    application = relationship("Application", back_populates="status_updates")
