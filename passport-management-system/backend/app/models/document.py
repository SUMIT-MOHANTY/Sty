from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"))
    document_type = Column(String)  # ID proof, address proof, etc.
    file_path = Column(String)
    upload_date = Column(DateTime, server_default=func.now())
    status = Column(String, default="Pending")  # Pending, Approved, Rejected

    # Relationships
    application = relationship("Application", back_populates="documents")
