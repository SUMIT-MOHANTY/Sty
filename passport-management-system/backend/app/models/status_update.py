from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base

class StatusUpdate(Base):
    __tablename__ = "status_updates"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"))
    status = Column(String)
    notes = Column(Text, nullable=True)
    updated_by = Column(String)  # Admin username or system
    timestamp = Column(DateTime, server_default=func.now())

    # Relationships
    application = relationship("Application", back_populates="status_updates")
