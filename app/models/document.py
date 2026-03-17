import uuid
from datetime import datetime
import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DocumentType(enum.Enum):
    passport_photo = "passport_photo"
    id_proof = "id_proof"
    address_proof = "address_proof"
    birth_certificate = "birth_certificate"
    other = "other"

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False, index=True)
    type = Column(Enum(DocumentType), nullable=False)
    file_path = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    application = relationship("Application", back_populates="documents")

    def __repr__(self):
        return f"<Document(id={self.id}, type={self.type}, application_id={self.application_id})>"
